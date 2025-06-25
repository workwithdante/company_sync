import frappe

def get_client():
    from typing import cast, TYPE_CHECKING
    if TYPE_CHECKING:
        from company_sync.company_sync.doctype.company_sync_settings.company_sync_settings import CompanySyncSettings
        
    conf = cast("CompanySyncSettings", frappe.get_doc("Company Sync Settings"))
    api_user = conf.user_api
    api_endpoint = conf.endpoint
    api_token = conf.get_password(r"token")
    
    if not api_user or not api_endpoint or not api_token:
        frappe.throw("API User, Endpoint, or Token is not set in Company Sync Settings.", title="Configuration Error")
    
    from crm_sync.crm_sync.doctype.vtigercrm_sync.api.WSClient import VTigerWSClient

    client = VTigerWSClient(api_endpoint)
    client.doLogin(api_user, api_token)

    return client