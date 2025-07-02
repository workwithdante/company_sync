from company_sync.database.engine import get_engine
import pandas as pd
import frappe
from frappe import _
from sqlalchemy import text
import msoffcrypto
import random
import os

class SyncProcessor:
	def __init__(self, csv_path: str, db_name):
		self.csv_path = csv_path
		self.db_name = db_name
	
	def read_csv(self) -> pd.DataFrame:
		csv_site_path = frappe.get_site_path(self.csv_path.lstrip('/'))
		[type] = csv_site_path.split('.')[-1:]
		if type == 'csv':
			df = pd.read_csv(csv_site_path)
		elif type in ('xls', 'xlsx'):
			password = "MIAMI123abc!"

			# Generar un nombre aleatorio para el archivo descifrado
			random_name = f"{random.randint(1000, 9999)}.xlsx"
			decrypted_file_path = os.path.join(os.path.dirname(csv_site_path), random_name)

			try:
				# Intenta leer el archivo normalmente
				df = pd.read_excel(csv_site_path, engine='openpyxl')
			except Exception as e:
				print(f"Error al leer el archivo con contraseña: {e}")
				
				# Si hay un error (probablemente debido a la contraseña), intentamos descifrarlo
				with open(csv_site_path, "rb") as f:
					file = msoffcrypto.OfficeFile(f)
					file.load_key(password=password)  # Cargar la contraseña
					with open(decrypted_file_path, "wb") as decrypted_file:
						file.decrypt(decrypted_file)  # Desbloquear el archivo

				# Ahora lee el archivo descifrado
				df = pd.read_excel(decrypted_file_path, engine='openpyxl')

		else:
			df = pd.DataFrame([])
		
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
