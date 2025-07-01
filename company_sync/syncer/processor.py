from company_sync.database.engine import get_engine
import pandas as pd
import frappe
from frappe import _
from sqlalchemy import text

class SyncProcessor:
	def __init__(self, csv_path: str, db_name):
		self.csv_path = csv_path
		self.db_name = db_name
	
	def read_csv(self) -> pd.DataFrame:
		csv_site_path = frappe.get_site_path(self.csv_path.lstrip('/'))
		df = pd.read_csv(csv_site_path)
		
		if df.empty:
			frappe.logger().info("CSV file is empty or not found at %s", csv_site_path)
			return pd.DataFrame([])

		return df

	def process(self):
		df = self.read_csv()
		
		if df.empty:
			frappe.throw(_("CSV file is empty or not found."), title=_("Empty CSV File"))
		
		
		try:
			if engine := get_engine():
				with engine.connect() as conn:
					conn.execute(text(f'TRUNCATE TABLE {self.db_name}.temp RESTART IDENTITY;'))
					conn.commit()
					
				df.to_sql(
					name='temp',
					schema=self.db_name,
					con=engine,
					if_exists='append',
					index=False,
					chunksize=1000
				)
				frappe.msgprint(
					_(f"DataFrame successfully written to '{self.db_name}.temp' table."), 
					title=_("Import Successfully")
				) 
				frappe.logger().info(f"DataFrame successfully written to '{self.db_name}' table.")
			else:
				frappe.throw(_("Database engine is not initialized."), title=_("Cannot write DataFrame")) 
				frappe.logger().error("Database engine is not initialized. Cannot write DataFrame.")
		except Exception as e:
			frappe.throw(_("Failed to write DataFrame to the database."), title=_("Database Write Error"))            
