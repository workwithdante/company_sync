# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
from typing import Self
from company_sync.database.engine import get_engine
import frappe
from frappe.model.document import Document
from frappe.utils import cint, now
from sqlalchemy import text


class CompanySyncStatusType(Document):
	def db_insert(self, *args, **kwargs):
		pass
	
	def delete(self, ignore_permissions=False, force=False, *, delete_permanently=False):
		pass

	def load_from_db(self) -> Self:
		[row] = self.get_status_type(name=self.name)
		#row.modified = now()
		super(Document, self).__init__(row)

		return self

	def db_update(self):
		self.update_status_type(self.name)

	@staticmethod
	def get_list(args):
		# 1. Recoge y normaliza los argumentos
		filters      = args.get("filters") or []
		start        = cint(args.get("limit_start")) or 0
		page_length  = cint(args.get("limit_page_length")) or 20
		as_list      = args.get("as_list")

		# 2. Carga todo el catálogo de status (tu lista de dicts)
		status = CompanySyncStatusType.get_status_type()

		# 3. Aplica cada filtro sobre esa lista
		for doctype, field, operator, value in filters:
			if doctype != "Company Sync Status Type":
				continue

			if field == "name":
				if operator.lower() == "in":
					status = [r for r in status if r.get("name") in value]
				elif operator in ("=", "=="):
					status = [r for r in status if r.get("name") == value]

			elif field == "error":
				# value aquí es 1 o True
				flag = bool(value)
				if operator in ("=", "=="):
					status = [r for r in status if bool(r.get("error")) is flag]
				elif operator.lower() == "in":
					status = [r for r in status if bool(r.get("error")) in value]

		# 4. Si as_list, devolvemos pares [name, error]
		if as_list:
			return [[r["name"], r.get("error", False)] for r in status]

		# 5. Si tenemos filtros, devolvemos todos los docs filtrados
		if filters:
			return [frappe.get_doc(r) for r in status]

		# 6. Si no hay filtros, aplicamos paginación y orden
		ordered = sorted(status, key=lambda r: r.get("name"))  # o tu propio order_by
		page    = ordered[start : start + page_length]
		return [frappe.get_doc(r) for r in page]

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass
	
	@staticmethod
	def get_status_type(name = None):
		rows = []
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				
				# Base de la consulta
				sql = """
					SELECT
						name,
						error
					FROM company.status_type
				"""
				params = {}
					
				if name:
					sql += " WHERE name = :name"
					params = {"name": name}

				results = conn.execute(text(sql), params).fetchall()
				for idx, r in enumerate(results, start=1):
					rows.append({
						"doctype": 'Company Sync Status Type',
						"parent": 'Company Sync Register',
						"owner": frappe.session.user,
						"modified_by": frappe.session.user,
						"name": r[0],
						"error": r[1],
						"creation": now(),
						"modified": now(),
						"status_type": r[0],
						#"parent": r[1],
						#"parenttype": "Company Sync Scheduler",
						#"parentfield": "sync_log",
						#"idx": idx,
					})
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		
		return rows

	@staticmethod
	def update_status_type(name = None):
		"""
		Marca todas las filas de status_results cuya batch_name coincide,
		escribiendo el texto de revisión.
		"""
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				result = conn.execute(
					text("""
						UPDATE company.status_type
						SET error = NULL
						WHERE name = :name
					"""),
					{"name": name}
				)
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		


