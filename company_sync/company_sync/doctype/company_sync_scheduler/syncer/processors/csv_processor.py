# File: company_sync/processors/csv_processor.py
from company_sync.company_sync.doctype.company_sync_scheduler.database.engine import get_engine
import pandas as pd
import logging
import frappe

class CSVProcessor:
    def __init__(self, csv_path: str, db_name):
        self.csv_path = csv_path
        self.db_name = db_name
        self.logger = logging.getLogger(__name__)
    
    def read_csv(self) -> pd.DataFrame:
        csv_site_path = frappe.get_site_path(self.csv_path.lstrip('/'))
        df = pd.read_csv(csv_site_path)
        if df.empty:
            self.logger.info("CSV is empty")
        return df

    def process(self) -> pd.DataFrame:
        df = self.read_csv()
        if df.empty:
            return df
        
        df.to_sql(
            name=self.db_name,
            con=get_engine(),
            if_exists='replace',
            index=False,
            chunksize=1000  # ajusta según tu memoria/red
        )

