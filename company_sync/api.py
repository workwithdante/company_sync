from company_sync.company_sync.doctype.company_sync_log.company_sync_log import CompanySyncLog

def load_sync_logs(doc, method):
    doc.set("sync_log", [])
    if not doc.sync_on:
        return

    rows = CompanySyncLog.get_sync_logs(batch_name=doc.name)
    doc.set("sync_log", rows)