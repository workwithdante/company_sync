# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
import json
from company_sync.company_sync.doctype.company_sync_scheduler.database.engine import get_engine
import frappe
from frappe.model.document import Document
from datetime import datetime
from sqlalchemy import text

class CompanySyncLog(Document):
	def db_insert(self):
		pass

	def delete(self):
		pass

	def load_from_db(self):
		[row] = self.get_sync_logs(log_name = self.name)
		#row.modified = now()
		super(Document, self).__init__(row)

	def db_update(self):
		self.update_sync_log(self.sync_on, self.log_id, self.review)

	@staticmethod
	def get_list(args):
		rows = CompanySyncLog.get_sync_logs()
		return rows

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass
	
	@staticmethod
	def get_sync_logs(batch_name=None, process_date=None, log_id=None, log_name=None, filters=[]):
		rows = []
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				
				# Base de la consulta
				sql = """
					SELECT
						id,
						batch_name,
						process_date,
						status,
						crm_data::text  AS crm_data,
						csv_data::text  AS csv_data,
						review
					FROM company.status_results
				"""
				params = {}
				
				if batch_name:
					ts_str = batch_name.split("Sync on ", 1)[1]
					process_date = process_date if process_date else datetime.fromisoformat(ts_str)
				
				if log_name:
					process_date = process_date if process_date else datetime.fromisoformat(log_name.rsplit('-', 1)[0])
					log_id = log_id if log_id else log_name.rsplit('-', 1)[1]
					
				if process_date and log_id:
					sql += " WHERE process_date = :process_date AND id = :log_id"
					params = {"process_date": process_date, "log_id": log_id}
					if filters:
						sql += " AND status IN :filters"
				elif filters:
					sql += " WHERE status IN :filters"
					params["filters"] = tuple(filters)
					
				sql += " ORDER BY process_date"

				results = conn.execute(text(sql), params).fetchall()
				for idx, r in enumerate(results, start=1):
					crm_json = json.loads(r[4] or "{}")
					csv_json = json.loads(r[5] or "{}")
					rows.append({
						"doctype": "Company Sync Log",
						"id": csv_json.get('member_id') or crm_json.get('so_no'),
						"log_id": r[0],
						"sync_on": r[2],
						"status": r[3],
						"name": f"{r[2]}-{r[0]}",
						"crm": json.dumps(crm_json, indent=4),
						"csv": json.dumps(csv_json, indent=4),
						"creation": r[2],
						"modified": r[2],
						"parent": r[1],
						"parenttype": "Company Sync Scheduler",
						"parentfield": "sync_log",
						"idx": idx,
						"review": r[6] or "",
					})
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		
		return rows

	@staticmethod
	def update_sync_log(sync_on: datetime, log_id: int, review: str):
		"""
		Marca todas las filas de status_results cuya batch_name coincide,
		escribiendo el texto de revisión.
		"""
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				result = conn.execute(
					text("""
						UPDATE company.status_results
						SET review = :review
						WHERE process_date = :process_date AND id = :log_id
					"""),
					{"process_date": sync_on, "log_id": log_id, "review": review}
				)
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		
