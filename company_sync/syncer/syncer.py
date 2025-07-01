from company_sync.database.engine import get_engine
from company_sync.database.unit_of_work import UnitOfWork
from company_sync.syncer.controller import SyncController
from company_sync.syncer.observer.frappe import FrappeProgressObserver
import frappe
from frappe import _
from typing import cast
from rq.timeouts import JobTimeoutException
from frappe.utils.background_jobs import enqueue, is_job_enqueued
from sqlalchemy.orm import sessionmaker

#from company_sync.overrides.exception.sync_error import SyncError
# Main Syncer class that orchestrates the VTiger CRM synchronization
class Syncer:
	from typing import TYPE_CHECKING
	if TYPE_CHECKING:
		from company_sync.company_sync.doctype.company_sync_register.company_sync_register import CompanySyncRegister
		
	def __init__(self, register: "CompanySyncRegister"):
		if not get_engine():
			frappe.logger().error("Database engine not initialized")
			return False

		# Initialize syncer with document name and required components
		self.progress_observer = FrappeProgressObserver()
		self.unit_of_work = UnitOfWork(lambda: sessionmaker(bind=get_engine())())
		self.job_id = f"company_sync_register::{register.name}"
		self.register = register

	def job_run(self):
		"""This method runs in background job"""
		try:
			controller = SyncController(self.register)

			if not is_job_enqueued(self.job_id):
				enqueue(
					controller.process,
					queue="default",
					timeout=10000,
					event="company_sync_register",
					job_id=self.job_id,
					company_sync_register=self.register.name,
					now=True,
				)
				return True
			else:
				frappe.throw(_("CSV file, company, or broker not set in the Company Sync Register."), title=_("Missing Information"))
		except JobTimeoutException:
			# Handle timeout
			frappe.db.rollback()
			doc = frappe.get_doc("Company Sync Register", str(self.register.name))
			doc.db_set("status", "Timed Out")
		except Exception as e:
			# Handle general errors
			self.progress_observer.updateError(f"Sync error: {str(e)}", {'register.name': self.register.name, "doctype": "Company Sync Register"}, event="company_sync_error_log", after_commit=False)
			frappe.db.rollback()
			doc = frappe.get_doc("Company Sync Register", str(self.register.name))
			doc.db_set("status", "Error")
			doc.log_error("Company Sync failed")
		finally:
			# Reset import flag
			frappe.flags.in_import = False
			#frappe.realtime()
			#frappe.db.commit
			doc = frappe.get_doc("Company Sync Register", str(self.register.name))
			doc.db_set("status", "Success")
	
	def worker(self):
		# Import register status check
		from frappe.utils.scheduler import is_scheduler_inactive

		# Determine if sync should run immediately
		run_now = frappe.flags.in_test or frappe.conf.developer_mode
		if is_scheduler_inactive() and not run_now:
			frappe.throw(_("register is inactive. Cannot import data."), title=_("register Inactive"))

		self.job_run()