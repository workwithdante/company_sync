import io
import psycopg
from psycopg import sql
from typing import Generator

def stream_to_postgres(conn: psycopg.Connection, df, table_name: str = "stg_policy_tmp"):
    """
    Envía un Polars DataFrame directamente a PostgreSQL vía COPY FROM STDIN (streaming).
    """
    buffer = io.StringIO()
    df.write_csv(buffer, separator=";", has_header=True)
    buffer.seek(0)
    
    with conn.cursor() as cur:
        cur.execute(sql.SQL(f"CREATE TEMP TABLE {table_name} (LIKE etl.stg_policy INCLUDING ALL) ON COMMIT DROP;"))
        copy_cmd = sql.SQL("COPY {} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';')").format(sql.Identifier(table_name))
        with cur.copy(copy_cmd) as copy:
            copy.write(buffer.read())
        cur.execute(sql.SQL("SELECT * FROM etl.merge_policy_from(%s::regclass);"), (table_name,))
    conn.commit()
