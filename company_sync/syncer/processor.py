# company_sync/etl_pipeline.py
from zipfile import BadZipFile
import polars as pl
import pandas as pd
import msoffcrypto
import io, os, random
import frappe
from frappe import _
from psycopg import sql
from company_sync.adapters.registry import get_adapter
from company_sync.database.engine import get_pg_conn  # SQLAlchemy engine

def _read_table(csv_site_path: str) -> pl.DataFrame:
    ext = os.path.splitext(csv_site_path)[1].lower()

    if ext == ".csv":
        return pl.read_csv(
            csv_site_path,
            separator=";",           # ajusta si tu CSV usa coma
            ignore_errors=True,
            null_values=["", "NULL", "null"],
        )

    if ext in (".xls", ".xlsx"):
        try:
            df_pd = pd.read_excel(csv_site_path, engine="openpyxl", dtype=str)
            return pl.from_pandas(df_pd.fillna(""))
        except BadZipFile:
            password = "MIAMI123abc!"
            tmp_path = os.path.join(os.path.dirname(csv_site_path), f"{random.randint(1000,9999)}.xlsx")
            with open(csv_site_path, "rb") as f:
                of = msoffcrypto.OfficeFile(f)
                of.load_key(password=password)
                with open(tmp_path, "wb") as out:
                    of.decrypt(out)
            try:
                df_pd = pd.read_excel(tmp_path, engine="openpyxl", dtype=str)
                return pl.from_pandas(df_pd.fillna(""))
            finally:
                try: os.remove(tmp_path)
                except: pass

    return pl.DataFrame([])

class SyncProcessor:
    """
    Lee (Polars/Pandas) -> adapta (adapter) -> COPY a TEMP stg_policy_tmp -> etl.merge_policy_from('stg_policy_tmp')
    """
    
    def __init__(self, csv_path: str, adapter_name: str, sep: str = ";"):
        self.csv_path = csv_path
        self.adapter_name = adapter_name
        self.sep = sep

    def read_any(self) -> pl.DataFrame:
        csv_site_path = frappe.get_site_path(self.csv_path.lstrip("/"))
        df = _read_table(csv_site_path)
        if df.is_empty():
            frappe.logger().info("CSV/Excel vacío o no encontrado en %s", csv_site_path)
            return pl.DataFrame([])
        return df

    def process(self):
        conn = None 
        df_raw = self.read_any()
        if df_raw.is_empty():
            frappe.throw(_("CSV/Excel vacío o no encontrado."), title=_("Archivo vacío"))

        adapter = get_adapter(self.adapter_name)
        df_norm = adapter.to_canonical_df(df_raw, source_name=self.csv_path)

        try:
            conn = get_pg_conn()
            if conn is None:
                frappe.throw(_("Database connection could not be established."), title=_("Connection Error"))

            # 🔽 Usar nombres distintos para evitar sombra de variables
            with conn.cursor() as cur:
                # Crear tabla temporal
                cur.execute("""
                    CREATE TEMP TABLE stg_policy_tmp
                    (LIKE etl.stg_policy INCLUDING ALL)
                    ON COMMIT DROP;
                """)

                # Serializar el DataFrame a memoria (buffer CSV)
                buf = io.StringIO()
                df_norm.write_csv(buf, separator=";", has_header=True)
                buf.seek(0)

                # COPY FROM STDIN (usa psycopg v3)
                copy_cmd = sql.SQL(
                    "COPY {} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';')"
                ).format(sql.Identifier("stg_policy_tmp"))

                with cur.copy(copy_cmd) as copy:
                    copy.write(buf.read())

                # Ejecutar la función SQL de merge
                cur.execute("SELECT * FROM etl.merge_policy_from('stg_policy_tmp'::regclass);")

            # Confirmar los cambios
            conn.commit()

            frappe.msgprint(
                _(f"✅ {len(df_norm)} filas importadas con adapter '{self.adapter_name}'."),
                title=_("Importación exitosa")
            )
            frappe.logger().info("DataFrame cargado y merge ejecutado. Filas=%s", len(df_norm))

        except Exception as e:
            frappe.logger().error("Error en COPY/MERGE: %s", e, exc_info=True)
            frappe.throw(_("Fallo al escribir en la base de datos."), title=_("Error de carga"))

        finally:
            if conn is not None:  # ✅ ya no da warning
                conn.close()