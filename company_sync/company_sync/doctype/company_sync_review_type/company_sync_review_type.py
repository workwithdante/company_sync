# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
from company_sync.company_sync.doctype.company_sync_scheduler.database.engine import get_engine
import frappe
from frappe.model.document import Document
from frappe.utils import now
from sqlalchemy import text


class CompanySyncReviewType(Document):
	
	def db_insert(self, *args, **kwargs):
		pass
	
	def delete(self):
		pass

	def load_from_db(self):
		[row] = self.get_review_type(name = self.name)
		#row.modified = now()
		super(Document, self).__init__(row)

	def db_update(self):
		self.update_review_type(self.name)

	@staticmethod
	def get_list(
		doctype,
		txt=None,
		searchfield=None,
		start=0,
		page_length=20,
		filters=None,
		as_list=False,               # <— acepta as_list
		reference_doctype=None,
		**kwargs
	):
		# 1) Saca TODOS los registros externos
		rows = CompanySyncReviewType.get_review_type()

		# 2) Filtrado por texto, solo si txt no está vacío
		if txt:
			rows = [r for r in rows if txt.lower() in r["name"].lower()]

		# 3) Paginación
		page = rows[start : start + page_length]

		# 4) Si vienen como lista (search_link pone as_list=True), devolver [[val, desc], …]
		if as_list or reference_doctype:
			return [[r["name"], r.get("error","")] for r in page]

		# 5) En cualquier otro caso (list view, reportview) devolver dicts
		if as_list:
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
	def get_review_type(name = None):
		rows = []
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				
				# Base de la consulta
				sql = """
					SELECT
						name,
						error
					FROM company.review_type
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
	def update_review_type(name = None):
		"""
		Marca todas las filas de review_results cuya batch_name coincide,
		escribiendo el texto de revisión.
		"""
		if engine := get_engine():
			# Usamos engine.begin() para commit automático
			with engine.begin() as conn:
				result = conn.execute(
					text("""
						UPDATE company.review_type
						SET error = NULL
						WHERE name = :name
					"""),
					{"name": name}
				)
		else:
			frappe.throw("No hay conexión a la base de datos externa.")
		


