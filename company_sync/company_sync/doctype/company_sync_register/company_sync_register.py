# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

from company_sync.company_sync.doctype.company_sync_log.company_sync_log import CompanySyncLog
import frappe
from company_sync.syncer.syncer import Syncer
from frappe.model.document import Document


class CompanySyncRegister(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Data
		broker: DF.Link
		csv_file: DF.Attach
		status_type: DF.TableMultiSelect
	
	def onload(self):
		filters = []

		if getattr(self, "status_type", None):
			# Si es una lista de dicts (por ejemplo, un Table MultiSelect)
			if isinstance(self.status_type, list):
				filters = [row.get("status_type") for row in self.status_type]
			else:
				# Si es solo un string (campo Link o Select)
				filters = [self.status_type]
    
		rows = CompanySyncLog.get_sync_logs(batch_name=self.name, filters=filters)
		self.sync_log = rows

@frappe.whitelist()
def start_sync(company_sync_register: str):
    from typing import cast
	# Start sync from form
    return Syncer(cast(CompanySyncRegister, frappe.get_doc("Company Sync Register", company_sync_register))).worker()