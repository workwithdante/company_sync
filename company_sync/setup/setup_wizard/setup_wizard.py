from frappe import _
from company_sync.setup.setup_wizard.operations import install_fixtures as fixtures
import frappe

def get_setup_stages(args):
    """Called by the framework to know whether to show your wizard."""
    from frappe.core.doctype.installed_applications.installed_applications import (
        get_setup_wizard_completed_apps,
    )

    # if already done, return no stages
    if "company_sync" in get_setup_wizard_completed_apps():
        return []

    # otherwise return a single stage whose `fn` will just return your slides_settings to the front end
    return [
		{
			"status": _("Setting item default"),
			"fail_msg": "Failed to set defaults",
			"tasks": [
				{
        			"fn": setup_company_sync_settings,
					"args": args,
     				"fail_msg": _("Failed to setup defaults"),
					"app_name": "company_sync",
			},
			],
		},
	]

def setup_company_sync_settings(args):
	fixtures.create_company_sync_settings(args)