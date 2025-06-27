# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

from company_sync.company_sync.doctype.company_sync_log.company_sync_log import CompanySyncLog
import frappe
from company_sync.syncer.syncer import Syncer
from frappe.model.document import Document
from datetime import datetime


class CompanySyncRegister(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Data
		broker: DF.Link
		csv_file: DF.Attach
		status_type: DF.TableMultiSelect
		status_log: DF.Table
	
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

		# 2) Únicos en orden
		all_statuses = [r.get("status") for r in rows]
		status_labels = list(dict.fromkeys(all_statuses))

		# 3) Consulta en bloque cuáles Status Type tienen error=True
		types_with_error = frappe.db.get_list(
			"Company Sync Status Type",
			filters={
				"name": ["in", status_labels],
				"error": 1
			},
			pluck="name"
		)
		#error_set = set(types_with_error if isinstance(types_with_error, list) else [types_with_error] )
		error_set = { doc.name for doc in types_with_error }

		# Mantén el orden original pero solo los que están en error_set
		filtered_labels = [s for s in status_labels if s in error_set]

		# 4) Reemplaza en memoria status_log antes de pintar
		existing = { child.status_type for child in self.status_log }

		# 3) Creamos e insertamos cada child row
		for label in filtered_labels:
			if label in existing:
				continue

			child = frappe.get_doc({
				"doctype":     "Company Sync Status Select",
				"status_type": label,
				"parent":      self.name,
				"parentfield": "status_log",
				"parenttype":  "Company Sync Register"
			}).insert(ignore_permissions=True)

			# 4) Lo agregamos a la lista en memoria para que el cliente lo vea inmediatamente
			self.status_log.append(child)
			
		self.sync_log = [frappe.get_doc(row) for row in rows] 

@frappe.whitelist()
def start_sync(company_sync_register: str):
	from typing import cast
	# Start sync from form
	return Syncer(cast(CompanySyncRegister, frappe.get_doc("Company Sync Register", company_sync_register))).worker()

@frappe.whitelist()
def update_sync_log(sync_on: str, log_id: int, review: str):
	sync_on_localtime = datetime.fromisoformat(sync_on)
	CompanySyncLog.update_sync_log(sync_on_localtime, log_id, review)