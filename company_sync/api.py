import frappe
from company_sync.company_sync.doctype.company_sync_scheduler.database.engine import get_engine

def load_sync_logs(doc, method):
    doc.set("sync_log", [])
    if not doc.sync_on:
        return

    if engine := get_engine():
            # suponiendo que self.unit_of_work es un Engine o Connection
        conn = engine.raw_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT process_date, status,
                    crm_data::text  AS crm_data,
                    csv_data::text  AS csv_data
                FROM company.status_results
                WHERE batch_name = %s
                ORDER BY process_date
            """, (doc.name,))
            rows = cursor.fetchall()
        finally:
            conn.close()

        for r in rows:
            row = doc.append("sync_log", {})
            row.process_date = r.process_date
            row.status       = r.status
            row.crm_data     = r.crm_data
            row.csv_data     = r.csv_data
