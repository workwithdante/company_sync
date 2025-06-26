# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
from company_sync.database.engine import get_engine
import frappe
from frappe.model.document import Document
from frappe.utils import now
from sqlalchemy import text


class CompanySyncStatusType(Document):
	def db_insert(self, *args, **kwargs):
		pass
	
	def delete(self):
		pass

	def load_from_db(self):
		[row] = self.get_status_type(name = self.name)
		#row.modified = now()
		super(Document, self).__init__(row)

	def db_update(self):
		self.update_status_type(self.name)

	@staticmethod
	def get_list(doctype, txt=None, searchfield=None, start=0,
             page_length=20, filters=None, as_dict=False, reference_doctype=None):
		# 1) Trae todos los registros del externo
		rows = CompanySyncStatusType.get_status_type()

		# 2) Filtra por texto si hace falta
		if txt:
			rows = [r for r in rows if txt.lower() in r["name"].lower()]

		# 3) Paginación estándar
		end = start + page_length
		page = rows[start:end]

		# 4) Devuelve en el formato que Frappe espera
		if as_dict:
			# [{ name, error, creation, modified }, …]
			return page
		else:
			# [[value, description], …]
			return [[r["name"], r.get("error", "")] for r in page]

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
						"name": r[0],
						"error": r[1],
						"creation": now(),
						"modified": now(),
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
		


