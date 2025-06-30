# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
import json
from typing import Counter, Self
from company_sync.database.engine import get_engine
import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.types.DF import Datetime
from frappe.utils import cint
from sqlalchemy import text

class CompanySyncLog(Document):
	from typing import TYPE_CHECKING
	if TYPE_CHECKING:
		from frappe.types import DF
		sync_on: DF.Datetime
		log_id: DF.Int
		status: DF.Data
		crm: DF.Text
		csv: DF.Text
		review: DF.Text
		
	def db_insert(self, ignore_if_duplicate=False):
		pass

	def delete(self, ignore_permissions=False, force=False, *, delete_permanently=False):
		pass

	def load_from_db(self) -> Self:
		[log] = self.get_sync_logs(log_name=self.name)
  
		super(Document, self).__init__(log)


		#review_row = self.get_sync_logs(log_id=self.name)
		#if review_row:
			# Ejemplo: asignar datos adicionales a atributos personalizados
			#self.review_type_data = review_row

		return self
	
	def db_update(self):
		self.update_sync_log(self.sync_on, self.log_id, self.review)

	@staticmethod
	def get_list(args):
		raw_filters = args.get("filters") or {}

		# Asegurar que filters sea un dict
		filters = raw_filters if isinstance(raw_filters, dict) else {}
  
		start = cint(args.get("limit_start")) or 0
		page_length = cint(args.get("limit_page_length")) or 20
		order_by = args.get("order_by") or "process_date desc"

		batch = filters.get("batch_name")
		log_id = filters.get("log_id")
		log_name = filters.get("name")
		status_filter = filters.get("status")

		logs = CompanySyncLog.get_sync_logs(
			batch_name=batch,
			log_id=log_id,
			log_name=log_name,
			filters=[status_filter] if status_filter else []
		)
  
		if args.get("as_list"):
			# Convertir a lista de listas
			return [[r.get('name'), r.get("status", ""), r.get("sync_on", ""), r.get("review", "")] for r in logs]

		if args.get("linked_table_counter") == Counter():
			total = len(logs)
			return [
				d | {"count": total}
				for d in logs[start : start + page_length]
			]

		# Paginar manualmente
		return [d for d in logs[start : start + page_length]]

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass
	
	@staticmethod
	def get_sync_logs(batch_name=None, process_date=None, log_id=None, log_name=None, filters=[], *args, **kwargs):
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
					
				if process_date:
					sql += " WHERE process_date = :process_date"
					params["process_date"] = process_date
		 
				if log_id:
					sql += " AND id = :log_id"
					params["log_id"] = log_id
	
				if filters:
					sql += " AND status IN :filters"
					params["filters"] = tuple(filters)
					
				sql += " ORDER BY id"

				results = conn.execute(text(sql), params).fetchall()
				for idx, r in enumerate(results, start=1):
					crm_json = json.loads(r[4] or "{}")
					csv_json = json.loads(r[5] or "{}")
					rows.append({
						"doctype": "Company Sync Log",
						"id": csv_json.get('member_id') or crm_json.get('so_no'),
						"idx": r[0],
						"log_id": r[0],
						"sync_on": r[2],
						"status": r[3],
						"name": f"{r[2]}-{r[0]}",
						"crm": json.dumps(crm_json, indent=4),
						"csv": json.dumps(csv_json, indent=4),
						"creation": r[2],
						"modified": r[2],
						"review": r[6] or "",
					})
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		
		return rows

	@staticmethod
	@frappe.whitelist()
	def update_sync_log(sync_on: Datetime, log_id: int, review: str):
		"""
		Marca todas las filas de status_results cuya batch_name coincide,
		escribiendo el texto de revisión.
		"""
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				conn.execute(
					text("""
						UPDATE company.status_results
						SET review = :review
						WHERE process_date = :process_date AND id = :log_id
					"""),
					{"process_date": sync_on, "log_id": log_id, "review": review}
				)
			print("HEre")
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		
