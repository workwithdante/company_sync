import frappe
from frappe import _
import datetime
from company_sync.database.engine import get_engine
from company_sync.database.unit_of_work import UnitOfWork
import psycopg2
import pandas as pd
from sqlalchemy.orm import sessionmaker
from company_sync.syncer.utils import update_logs, progress_observer


class SyncUpdater:
    def __init__(self, vtiger_client, company: str, broker: int, doc_name: str):
        self.vtiger_client = vtiger_client
        self.company = company
        self.broker = broker
        self.doc_name = doc_name
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
            frappe.logger().error(f"Error updating memberID {memberID}: {e}")
            return None

    def process_order(self, row):
        status = row.iloc[0]
        json_crm = row.iloc[1] or {}
        json_csv = row.iloc[2] or {}
        memberID = json_csv.get('member_id')
        paidThroughDate = json_csv.get('paid_through_date', '')
        
        salesorder_no = json_crm.get('so_no')
        
        if memberID and salesorder_no and status in ('Update'):
            self.update_sales_order(memberID, paidThroughDate, salesorder_no)
        else:
            update_logs(self.doc_name, memberID, self.company, self.broker, status)
            

    def update_orders(self):
        if engine := get_engine():
            # suponiendo que self.unit_of_work es un Engine o Connection
            conn = engine.raw_connection()
            try:
                cursor = conn.cursor()
                ts_str = self.doc_name.split("Sync on ", 1)[1]
                process_date = datetime.datetime.fromisoformat(ts_str)
                
                
                try:
                    cursor.callproc("company.get_status_by", (self.company, self.broker, self.doc_name, process_date))
                except psycopg2.Error as e:
                    frappe.logger().error(
                        f"Error calling stored procedure 'company.get_status_by' "
                        f"with args (company={self.company}, broker={self.broker}, doc_name={self.doc_name}, process_date={process_date}):\n"
                        f"{type(e).__name__}: {e.pgerror or e}")
                    
                    frappe.throw(
                        _("Error calling stored procedure 'company.get_status_by'. Please check the logs for more details."),
                        title=_("Database Error"))
                    # Log the error using frappe logger
                    raise e
                except Exception as e:
                    frappe.throw(
                        _("An unexpected error occurred while calling the stored procedure 'company.get_status_by'. Please check the logs for more details."),
                        title=_("Unexpected Error"))
                    raise e from e

                # Si devuelve datos
                results = cursor.fetchall()
                df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
                
                total = cursor.rowcount
                #for i, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df), desc="Validando Órdenes de Venta 2..."), start=1):
                #    self.process_order(row)
                    # Calcula el progreso en porcentaje
                #    progress = float(i / total)
                    # Guarda el progreso en caché
                #    progress_observer.update(progress, {'doc_name': self.doc_name, 'doctype': 'Company Sync Scheduler'}, event='company_sync_refresh', after_commit=False)
                
                progress_observer.updateSuccess({'success': True, 'doc_name': self.doc_name, 'doctype': 'Company Sync Scheduler'}, event='company_sync_success', after_commit=False)

                cursor.close()
                conn.commit()
            except Exception as e:
                frappe.logger().error(f"Error during SO update: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()