# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
from company_sync.company_sync.doctype.company_sync_log.company_sync_log import CompanySyncLog
from frappe.model.document import Document

class CompanySyncLogItem(CompanySyncLog, Document):
	@property
	def sync_on(self):
		return self.parent

	@property
	def log_id(self):
		return self.memberid
	
	def onload(self):
		"""
		Load the document from the database.
		"""
		# This method can be used to load additional data if needed
		# For now, it does nothing
		pass

	def on_update(self):
		pass

	def db_update(self, *args, **kwargs):
        # esto llamará al db_update de CompanySyncLog, que ahora
        # encontrará self.sync_on y self.log_id válidos
		super().db_update(*args, **kwargs)

	def validate(self):
		"""
		Validate the document before saving.
		This method can be used to enforce any business rules or constraints.
		"""
		# For now, it does nothing
		pass