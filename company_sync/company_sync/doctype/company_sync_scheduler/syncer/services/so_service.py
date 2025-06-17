# File: company_sync/services/sales_order_service.py
from company_sync.company_sync.doctype.company_sync_scheduler.syncer.processors.csv_processor import CSVProcessor
from company_sync.company_sync.doctype.company_sync_scheduler.syncer.handlers.so_updater import SOUpdater

class SOService:
    def __init__(self, csv_path: str, company: str, broker: str, vtiger_client, doc_name, logger):
        self.csv_processor = CSVProcessor(csv_path, f"{company.lower()}.{''.join(b[0] for b in broker.split() if b).lower()}")
        self.so_updater = SOUpdater(vtiger_client, company, broker, doc_name, logger=logger)

    def process(self):
        self.csv_processor.process()
        self.so_updater.update_orders()
