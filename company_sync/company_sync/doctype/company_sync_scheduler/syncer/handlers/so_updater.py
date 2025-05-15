# File: company_sync/handlers/so_updater.py
import datetime
import logging
from company_sync.company_sync.doctype.company_sync_scheduler.database.engine import get_engine
from company_sync.company_sync.doctype.company_sync_scheduler.database.unit_of_work import UnitOfWork
from sqlalchemy import text
import pandas as pd
from sqlalchemy.orm import sessionmaker
from company_sync.company_sync.doctype.company_sync_scheduler.syncer.utils import last_day_of_month, update_logs, progress_observer
from tqdm import tqdm

class SOUpdater:
    def __init__(self, vtiger_client, company: str, data_config: dict, broker: str, doc_name: str, logger=None):
        self.vtiger_client = vtiger_client
        self.company = company
        self.data_config = data_config
        self.broker = broker
        self.doc_name = doc_name
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.unit_of_work = UnitOfWork(lambda: sessionmaker(bind=get_engine())())
    
    def update_sales_order(self, memberID: str, paidThroughDate: str, salesorder_no: dict):
        try:
            def getSOAllData(salesorder_no, memberID):
                query_sales = f"SELECT * FROM SalesOrder WHERE salesorder_no = '{salesorder_no}' AND cf_2119 = '{memberID}' LIMIT 1;"
                salesOrderData = self.vtiger_client.doQuery(query_sales)
                return salesOrderData
            
            [salesOrderData] = getSOAllData(salesorder_no, memberID)

            if paidThroughDate > salesOrderData.get('cf_2261'):
                salesOrderData['cf_2261'] = paidThroughDate
                salesOrderData['productid'] = '14x29415'
                salesOrderData['assigned_user_id'] = '19x113'
                salesOrderData['LineItems'] = {
                    'productid': '14x29415',
                    'listprice': '0',
                    'quantity': '1'
                }
                return self.vtiger_client.doUpdate(salesOrderData)
        except Exception as e:
            self.logger.error(f"Error updating memberID {memberID}: {e}")
            return None

    def process_order(self, row):
        memberID = str(row['member_id'])
        paidThroughDate = str(row.get('Pago_Hasta', ''))
        status = str(row['estado'])
        salesorder_no = str(row['so_no'])
        
        if status == 'Paid':
            self.update_sales_order(memberID, paidThroughDate, salesorder_no)
        elif status == 'Problem':
            update_logs(self.doc_name, memberID, self.company, self.broker, status)

    def update_orders(self):
        # suponiendo que self.unit_of_work es un Engine o Connection
        sql = "CALL get_status(%s, %s)"
        df = pd.read_sql(sql,
            con=get_engine(), 
            params=(self.company, self.broker))

        total = len(df)
        for i, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df), desc="Validando Órdenes de Venta 2..."), start=1):
            self.process_order(row)
            # Calcula el progreso en porcentaje
            progress = float(i / total)
            # Guarda el progreso en caché
            progress_observer.update(progress, {'doc_name': self.doc_name, 'doctype': 'Company Sync Scheduler'}, event='company_sync_refresh')
        
        progress_observer.updateSuccess({'success': True, 'doc_name': self.doc_name, 'doctype': 'Company Sync Scheduler'})
