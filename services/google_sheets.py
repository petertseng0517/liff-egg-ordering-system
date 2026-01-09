"""
Google Sheets 服務模組
"""
import gspread
from google.oauth2.service_account import Credentials
import logging
from config import Config
from datetime import datetime
import pytz
import re
import json

logger = logging.getLogger(__name__)

# 台灣時區
TW_TZ = pytz.timezone(Config.TIMEZONE)


class GoogleSheetsService:
    """Google Sheets 連線與操作服務"""
    
    _client = None
    _spreadsheet = None
    
    @classmethod
    def init(cls):
        """初始化 Google Sheets 連線"""
        try:
            creds = Credentials.from_service_account_file(
                'service_account.json',
                scopes=Config.GOOGLE_SHEETS_SCOPES
            )
            cls._client = gspread.authorize(creds)
            cls._spreadsheet = cls._client.open_by_key(Config.SPREADSHEET_ID)
            logger.info("Google Sheets connection initialized successfully")
        except Exception as e:
            logger.error(f"Google Sheets initialization error: {e}")
            raise
    
    @classmethod
    def get_sheet(cls, sheet_name):
        """取得特定工作表"""
        if cls._spreadsheet is None:
            cls.init()
        
        try:
            return cls._spreadsheet.worksheet(sheet_name)
        except Exception as e:
            logger.error(f"Error getting sheet '{sheet_name}': {e}")
            return None
    
    @classmethod
    def add_member(cls, user_id, name, phone, address, birth_date=None, address2=None):
        """新增會員記錄"""
        try:
            sheet = cls.get_sheet("Members")
            # 電話號碼前加單引號確保以文本存儲，避免丟失前導零
            phone_str = f"'{phone}" if phone else ""
            sheet.append_row([user_id, name, phone_str, address, birth_date or "", address2 or ""])
            logger.info(f"Member added: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return False
    
    @classmethod
    def update_member(cls, user_id, name, phone, address, address2=""):
        """更新會員資料"""
        try:
            sheet = cls.get_sheet("Members")
            cell = sheet.find(user_id)
            if not cell:
                return False
            
            # 更新對應欄位
            sheet.update_cell(cell.row, 2, name)      # B欄：姓名
            # 電話號碼前加單引號確保以文本存儲，避免丟失前導零
            phone_str = f"'{phone}" if phone else ""
            sheet.update_cell(cell.row, 3, phone_str) # C欄：電話
            sheet.update_cell(cell.row, 4, address)   # D欄：地址1
            sheet.update_cell(cell.row, 6, address2)  # F欄：地址2
            
            logger.info(f"Member updated: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating member: {e}")
            return False
    
    @classmethod
    def check_member_exists(cls, user_id):
        """檢查會員是否存在"""
        try:
            sheet = cls.get_sheet("Members")
            cell = sheet.find(user_id)
            if cell:
                row_values = sheet.row_values(cell.row)
                return {
                    "userId": row_values[0] if len(row_values) > 0 else "",
                    "name": row_values[1] if len(row_values) > 1 else "",
                    "phone": row_values[2] if len(row_values) > 2 else "",
                    "address": row_values[3] if len(row_values) > 3 else "",
                    "birthDate": row_values[4] if len(row_values) > 4 else "",
                    "address2": row_values[5] if len(row_values) > 5 else ""
                }
            return None
        except Exception as e:
            logger.error(f"Error checking member: {e}")
            return None
    
    @classmethod
    def add_order(cls, order_id, user_id, item_str, amount, status, payment_status, payment_method):
        """新增訂單"""
        try:
            sheet = cls.get_sheet("Orders")
            sheet.append_row([
                order_id,
                user_id,
                item_str,
                amount,
                datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                status,
                "",  # DeliveryLogs (JSON)
                payment_status,
                payment_method
            ])
            logger.info(f"Order added: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return False
    
    @classmethod
    def get_user_orders(cls, user_id):
        """取得使用者訂單"""
        try:
            sheet = cls.get_sheet("Orders")
            all_records = sheet.get_all_values()
            
            orders = []
            for row in all_records[1:]:  # Skip header
                if len(row) > 1 and row[1] == user_id:
                    orders.append({
                        "orderId": row[0],
                        "items": row[2],
                        "amount": row[3],
                        "date": row[4],
                        "status": row[5],
                        "paymentStatus": row[7] if len(row) > 7 else "未付款",
                        "paymentMethod": row[8] if len(row) > 8 else "未指定"
                    })
            return orders
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    @classmethod
    def get_all_orders_with_members(cls):
        """取得所有訂單並併入會員信息"""
        try:
            # 取得會員資料
            member_sheet = cls.get_sheet("Members")
            members_data = member_sheet.get_all_values()
            member_map = {}
            
            for row in members_data[1:]:
                if len(row) > 0:
                    member_map[row[0]] = {
                        "name": row[1] if len(row) > 1 else "",
                        "phone": row[2] if len(row) > 2 else "",
                        "address": row[3] if len(row) > 3 else "",
                        "birthDate": row[4] if len(row) > 4 else "",
                        "address2": row[5] if len(row) > 5 else ""
                    }
            
            # 取得訂單資料
            order_sheet = cls.get_sheet("Orders")
            orders_data = order_sheet.get_all_values()
            
            results = []
            for row in orders_data[1:]:
                if len(row) < 6:
                    continue
                
                uid = row[1]
                customer = member_map.get(uid, {})
                
                # 解析出貨日誌
                logs = []
                if len(row) > 6 and row[6]:
                    try:
                        logs = json.loads(row[6])
                    except:
                        logs = []
                
                results.append({
                    "orderId": row[0],
                    "userId": uid,
                    "items": row[2],
                    "amount": row[3],
                    "date": row[4],
                    "status": row[5],
                    "deliveryLogs": logs,
                    "paymentStatus": row[7] if len(row) > 7 else "未付款",
                    "paymentMethod": row[8] if len(row) > 8 else "未指定",
                    "customer": customer
                })
            
            return results
        except Exception as e:
            logger.error(f"Error getting all orders: {e}")
            return []
    
    @classmethod
    def update_order_payment_status(cls, order_id, payment_status):
        """更新訂單付款狀態"""
        try:
            sheet = cls.get_sheet("Orders")
            cell = sheet.find(order_id)
            if cell:
                sheet.update_cell(cell.row, 8, payment_status)  # Column H
                logger.info(f"Order {order_id} payment status updated to {payment_status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    @classmethod
    def add_delivery_log(cls, order_id, qty, address=""):
        """新增出貨紀錄"""
        try:
            sheet = cls.get_sheet("Orders")
            cell = sheet.find(order_id)
            if not cell:
                return False, "訂單不存在"
            
            # 取得現有日誌
            row_values = sheet.row_values(cell.row)
            current_logs_str = row_values[6] if len(row_values) > 6 else "[]"
            
            try:
                logs = json.loads(current_logs_str)
                if not isinstance(logs, list):
                    logs = []
            except:
                logs = []
            
            # 新增日誌
            new_log = {
                "date": datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M"),
                "qty": qty,
                "address": address
            }
            logs.append(new_log)
            
            # 計算新狀態
            total_delivered = sum(int(l['qty']) for l in logs)
            # 從 item 中解析總數
            items_str = row_values[2] if len(row_values) > 2 else ""
            match = re.search(r'x(\d+)', items_str)
            total_ordered = int(match.group(1)) if match else 1
            
            new_status = "已完成" if total_delivered >= total_ordered else "部分配送"
            
            # 更新工作表
            sheet.update_cell(cell.row, 6, new_status)
            sheet.update_cell(cell.row, 7, json.dumps(logs, ensure_ascii=False))
            
            logger.info(f"Delivery log added for order {order_id}")
            # 返回包含更多信息的結果，避免需要重新查詢
            return True, {
                "status": new_status,
                "total_delivered": total_delivered,
                "total_ordered": total_ordered,
                "delivery_date": new_log["date"]
            }
        except Exception as e:
            logger.error(f"Error adding delivery log: {e}")
            return False, str(e)
    
    @classmethod
    def correct_delivery_log(cls, order_id, log_index, new_qty, new_address, admin_name, reason):
        """修正出貨紀錄（不刪除，而是記錄修正）"""
        try:
            sheet = cls.get_sheet("Orders")
            cell = sheet.find(order_id)
            if not cell:
                return False, "訂單不存在"
            
            # 取得現有日誌
            row_values = sheet.row_values(cell.row)
            current_logs_str = row_values[6] if len(row_values) > 6 else "[]"
            
            try:
                logs = json.loads(current_logs_str)
                if not isinstance(logs, list):
                    logs = []
            except:
                logs = []
            
            if log_index < 0 or log_index >= len(logs):
                return False, "出貨紀錄索引無效"
            
            # 記錄修改前的數值
            old_log = logs[log_index]
            old_qty = int(old_log.get('qty', 0))
            old_address = old_log.get('address', '')
            
            # 更新日誌
            old_log['corrected'] = True
            old_log['correction_time'] = datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M")
            old_log['correction_admin'] = admin_name
            old_log['correction_reason'] = reason
            old_log['original_qty'] = old_qty
            old_log['corrected_qty'] = new_qty
            old_log['original_address'] = old_address
            old_log['address'] = new_address
            
            # 新增修正記錄到審計日誌
            cls._add_audit_log(order_id, "correct", admin_name, old_qty, new_qty, reason)
            
            # 計算新狀態（基於修正後的總數）
            total_delivered = sum(int(l.get('corrected_qty') or l.get('qty', 0)) for l in logs)
            items_str = row_values[2] if len(row_values) > 2 else ""
            match = re.search(r'x(\d+)', items_str)
            total_ordered = int(match.group(1)) if match else 1
            
            new_status = "已完成" if total_delivered >= total_ordered else "部分配送"
            
            # 更新工作表
            sheet.update_cell(cell.row, 6, new_status)  # 狀態欄
            sheet.update_cell(cell.row, 7, json.dumps(logs, ensure_ascii=False))  # 日誌欄
            
            logger.info(f"Delivery log corrected for order {order_id}: {old_qty} -> {new_qty} by {admin_name}")
            return True, {
                "old_qty": old_qty,
                "new_qty": new_qty,
                "status": new_status,
                "total_delivered": total_delivered,
                "total_ordered": total_ordered,
                "delivery_date": old_log.get('date', '')
            }
            
        except Exception as e:
            logger.error(f"Error correcting delivery log: {e}")
            return False, str(e)
    
    @classmethod
    def _add_audit_log(cls, order_id, operation, admin_name, before_value, after_value, reason):
        """新增審計日誌"""
        try:
            import json
            
            sheet = cls.get_sheet("DeliveryAuditLog")
            if not sheet:
                logger.warning("DeliveryAuditLog sheet not found, creating one...")
                # 如果工作表不存在，會在下方建立
                return False
            
            timestamp = datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([
                timestamp,
                order_id,
                operation,
                admin_name,
                before_value,
                after_value,
                reason,
                ""
            ])
            logger.info(f"Audit log added: {operation} on {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding audit log: {e}")
            return False
    
    @classmethod
    def get_delivery_audit_logs(cls, order_id):
        """取得特定訂單的審計日誌"""
        try:
            import json
            
            sheet = cls.get_sheet("DeliveryAuditLog")
            if not sheet:
                return []
            
            # 查詢所有該訂單的記錄
            all_records = sheet.get_all_records()
            order_logs = [r for r in all_records if r.get('訂單編號') == order_id or r.get('B') == order_id]
            
            return order_logs
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    @classmethod
    def update_order_status(cls, order_id, status):
        """更新訂單狀態"""
        try:
            sheet = cls.get_sheet("Orders")
            cell = sheet.find(order_id)
            if cell:
                sheet.update_cell(cell.row, 6, status)  # Column F
                logger.info(f"Order {order_id} status updated to {status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False



import re
