# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

from typing import OrderedDict
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
  
	def before_insert(self):
		"""Se ejecuta únicamente *antes* de la primera inserción en la BD."""
		self._populate_status_log()

	def _populate_status_log(self):
		# 1) Trae todos los tipos con error=1 de golpe
		error_statuses = set(frappe.get_all(
			"Company Sync Status Type",
			filters={"error": 1},
			pluck="name"
		))

		# 2) Lleva un set de los que ya añadiste (para no duplicar)
		existing = set()

		# 3) Recorre UNA vez los logs y añade el hijo la primera vez que ve cada status
		for row in CompanySyncLog.get_sync_logs(batch_name=self.name):
			status = row["status"]
			if status in error_statuses and status not in existing:
				self.append("status_log", {"status_type": status})
				existing.add(status)
	
	def onload(self):
		"""
		En onload sólo levantamos `sync_log` desde la BD, 
		y dejamos que el framework muestre los status_log que ya creó before_insert.
		"""
		# Arma filtros según lo que el usuario guardó en status_log
		filters = [d.status_type for d in (self.status_log or [])]

		# Consulta los logs (ya no tocamos status_log aquí)
		rows = CompanySyncLog.get_sync_logs(batch_name=self.name, filters=filters)

		# Sólo levanta sync_log para el UI
		self.sync_log = [frappe.get_doc(r) for r in rows]


@frappe.whitelist()
def start_sync(company_sync_register: str):
	from typing import cast
	# Start sync from form
	return Syncer(cast(CompanySyncRegister, frappe.get_doc("Company Sync Register", company_sync_register))).worker()

@frappe.whitelist()
def update_sync_log(sync_on: str, log_id: int, review: str):
	sync_on_localtime = datetime.fromisoformat(sync_on)
	CompanySyncLog.update_sync_log(sync_on_localtime, log_id, review)