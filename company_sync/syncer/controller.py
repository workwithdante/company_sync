import frappe
from frappe import _
from company_sync.database.client import get_client
from company_sync.syncer.processor import SyncProcessor
from company_sync.syncer.updater import SyncUpdater
import pandas as pd
from sqlalchemy import text

class SyncController:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from company_sync.company_sync.doctype.company_sync_register.company_sync_register import CompanySyncRegister
        
    def __init__(self, register: "CompanySyncRegister"):
        csv_file = register.csv_file
        company = register.company.lower()
        broker = self.get_broker_code(register.broker)
        doc_name = str(register.name)
        
        if not broker:
            return frappe.throw(_("Broker code not found for the provided broker name."), title=_("Missing Broker Code"))
            
        vtiger_client = get_client()
                       
        self.processor = SyncProcessor(csv_file, company)
        self.updater = SyncUpdater(vtiger_client, company, broker, doc_name)

    def process(self):
        self.processor.process()
        self.updater.update_orders()
    
    def get_broker_code(self, broker: str) -> int | None:
        """Get the broker code based on the broker name."""
        from typing import cast, TYPE_CHECKING
        if TYPE_CHECKING:
            from frappe.contacts.doctype.contact.contact import Contact
            class CustomContact(Contact):
                custom_national_producer_number: str

        broker_contact = cast("CustomContact", frappe.get_doc("Contact", broker))
        broker_npn = int(broker_contact.custom_national_producer_number)
        
        return broker_npn
