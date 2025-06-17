import frappe
from company_sync.company_sync.overrides.exception.sync_error import SyncError
from sqlalchemy.orm import sessionmaker

from company_sync.company_sync.doctype.company_sync_scheduler.database.engine import get_engine
from company_sync.company_sync.doctype.company_sync_scheduler.database.client import get_client
from company_sync.company_sync.doctype.company_sync_scheduler.syncer.observer.frappe import FrappeProgressObserver
from company_sync.company_sync.doctype.company_sync_scheduler.syncer.services.so_service import SOService

#from company_sync.overrides.exception.sync_error import SyncError
from company_sync.company_sync.doctype.company_sync_scheduler.config.logging import setup_logging

from company_sync.company_sync.doctype.company_sync_scheduler.database.unit_of_work import UnitOfWork

# Main Syncer class that orchestrates the VTiger CRM synchronization
class Syncer:
    def __init__(self, doc_name):
        if not get_engine():
            frappe.logger().error("Database engine not initialized")
            return False
        
        
        # Initialize syncer with document name and required components
        self.doc_name = doc_name
        self.vtigercrm_sync = frappe.get_doc("Company Sync Scheduler", doc_name)
        self.progress_observer = FrappeProgressObserver()
        self.unit_of_work = UnitOfWork(lambda: sessionmaker(bind=get_engine())())

    def sync(self):        
        try:
            logger = setup_logging()
            
            company = self.vtigercrm_sync.company
            broker = self.vtigercrm_sync.broker
            csv = self.vtigercrm_sync.company_file
            
            vtiger_client = get_client()
            
            service = SOService(csv, company, broker, vtiger_client, self.doc_name, logger)
            service.process()                
        except Exception as e:
            frappe.logger().error(f"Sync error: {str(e)}")
            
            self.progress_observer.updateError(f"Sync error: {str(e)}", {'doc_name': self.doc_name, "doctype": "Company Sync Scheduler"}, event="company_sync_error_log", after_commit=False)
            raise