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
		status_log: DF.TableMultiSelect
		sync_log: DF.Table
	
	def onload(self):
		filters = []
		self.sync_log = []
		
		# 1) Trae todas las Status Type que tienen error=1 (sin mirar rows)
		raw = frappe.get_all(
			"Company Sync Status Type",
			filters={"error": 1},
			fields=["name"]
		)

		error_statuses = { d.name for d in raw }

		# 2) Prepara el set de los status_type ya añadidos
		existing = {c.status_type for c in self.status_log}

		# 3) Arranca sync_log vacío
		self.sync_log = []

		# 4) Recorre rows UNA SOLA VEZ
		for row in CompanySyncLog.get_sync_logs(batch_name=self.name, filters=filters):
			status = row["status"]

			if status not in error_statuses | existing:
				continue

			if status not in existing:
				self.append("status_log", {
					"status_type": status
				})
				existing.add(status)

			# 4c) Añadimos ese row a sync_log
			self.append("sync_log", {
       			"id":           row["id"],
                "idx":           row["idx"],
                #"log_id": 		row["idx"],
                "status":       status,
                "csv":			row["csv"],
                "crm":			row["crm"],
                "review":       row.get("review", ""),
                "description":  row.get("description", ""),
                "sync_on":      row["sync_on"],
            })
   
def start_sync(company_sync_register: str):
	from typing import cast
	# Start sync from form
	return Syncer(cast(CompanySyncRegister, frappe.get_doc("Company Sync Register", company_sync_register))).worker()

@frappe.whitelist()
def update_sync_log(sync_on: str, log_id: int, review = None, description = None):
	sync_on_localtime = datetime.fromisoformat(sync_on)
	if review is not None:
		CompanySyncLog.update_sync_log(sync_on_localtime, log_id, review=review)
	
	if description is not None:
		CompanySyncLog.update_sync_log(sync_on_localtime, log_id, description=description)