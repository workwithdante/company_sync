import frappe
from .base import ProgressObserver

class FrappeProgressObserver(ProgressObserver):
    def update(self, percentage: float, context: dict, event = 'vtigercrm_sync_refresh'):
        frappe.publish_realtime(
            event,
            {
                'percentage': f"{percentage * 100:.2f}",
                'vtigercrm_sync': context['doc_name'],
            },
            doctype=context['doctype'],
            docname=context['doc_name'],
            after_commit=True,
        )
    
    def updateError(self, error_log: str, context: dict, event = 'vtigercrm_sync_error_log'):
        frappe.publish_realtime(
            event,
            {
                'error_log': error_log,
                'vtigercrm_sync': context['doc_name'],
            },
            doctype=context['doctype'],
            docname=context['doc_name'],
            after_commit=True,
        )
    
    def updateLog(self, context: dict, event = 'vtigercrm_sync_error_log'):
        frappe.publish_realtime(
            event,
            {
                'error_log': context['message'],
                'memberID': context['memberID'],
                'company': context['company'],
                'broker': context['broker']
            },
            doctype=context['doctype'],
            docname=context['doc_name'],
            after_commit=True,
        )
    
    
    def updateSuccess(self, context: dict, event = 'vtigercrm_sync_success'):
        frappe.publish_realtime(
            event,
            {
                'success': context['success'],
            },
            doctype=context['doctype'],
            docname=context['doc_name'],
            after_commit=True,
        )


