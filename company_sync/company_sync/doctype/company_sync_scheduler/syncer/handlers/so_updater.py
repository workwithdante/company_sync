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
    def __init__(self, vtiger_client, company: str, broker: str, doc_name: str, logger=None):
        self.vtiger_client = vtiger_client
        self.company = company
        self.broker = broker
        self.doc_name = doc_name
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.unit_of_work = UnitOfWork(lambda: sessionmaker(bind=get_engine())())
    
    def update_sales_order(self, memberID: str, paidThroughDate: str, salesorder_no: dict):
        try:
            salesOrderData = {}
            
            def getSOAllData(salesorder_no, memberID):
                query_sales = f"SELECT * FROM SalesOrder WHERE salesorder_no = '{salesorder_no}' AND cf_2119 = '{memberID}' LIMIT 1;"
                salesOrderData = self.vtiger_client.doQuery(query_sales)
                return salesOrderData
            
            if pack := getSOAllData(salesorder_no, memberID):
                [salesOrderData] = pack

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
        status = row.iloc[0]
        json_str = row.iloc[1]
        memberID = json_str.get('member_id')
        paidThroughDate = json_str.get('paid_through_date_csv', '')
        
        salesorder_no = json_str.get('so_no')
        
        if status in ('Paid'):
            self.update_sales_order(memberID, paidThroughDate, salesorder_no)
        else:
            update_logs(self.doc_name, memberID, self.company, self.broker, status)
            

    def update_orders(self):
        if engine := get_engine():
            # suponiendo que self.unit_of_work es un Engine o Connection
            conn = engine.raw_connection()
            try:
                cursor = conn.cursor()
                cursor.callproc("company.get_status_by", (self.company, self.broker))

                # Si devuelve datos
                results = cursor.fetchall()
                df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
                
                total = cursor.rowcount
                for i, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df), desc="Validando Órdenes de Venta 2..."), start=1):
                    self.process_order(row)
                    # Calcula el progreso en porcentaje
                    progress = float(i / total)
                    # Guarda el progreso en caché
                    progress_observer.update(progress, {'doc_name': self.doc_name, 'doctype': 'Company Sync Scheduler'}, event='company_sync_refresh', after_commit=False)
                
                progress_observer.updateSuccess({'success': True, 'doc_name': self.doc_name, 'doctype': 'Company Sync Scheduler'}, event='company_sync_success', after_commit=False)

                cursor.close()
                conn.commit()
            except Exception as e:
                self.logger.error(f"Error during SO update: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()