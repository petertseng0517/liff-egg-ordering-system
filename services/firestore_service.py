"""
Firebase Firestore 服務模組
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

# 台灣時區
TW_TZ = pytz.timezone(Config.TIMEZONE)


class FirestoreService:
    """Firebase Firestore 連線與操作服務"""
    
    _db = None
    
    @classmethod
    def init(cls):
        """初始化 Firebase 連線"""
        try:
            if not firebase_admin._apps:
                # 使用環境變數初始化
                creds_dict = {
                    "type": "service_account",
                    "project_id": Config.FIREBASE_PROJECT_ID,
                    "private_key": Config.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if Config.FIREBASE_PRIVATE_KEY else None,
                    "client_email": Config.FIREBASE_CLIENT_EMAIL,
                    "client_id": Config.FIREBASE_CLIENT_ID,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                }
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
            
            cls._db = firestore.client()
            logger.info("Firebase Firestore initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    @classmethod
    def add_member(cls, user_id, name, phone, address, birth_date=None, address2=None):
        """新增會員"""
        try:
            cls._db.collection('members').document(user_id).set({
                'userId': user_id,
                'name': name,
                'phone': phone,
                'address': address,
                'birthDate': birth_date or '',
                'address2': address2 or '',
                'createdAt': datetime.now(TW_TZ),
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Member added: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return False
    
    @classmethod
    def check_member_exists(cls, user_id):
        """檢查會員是否存在"""
        try:
            doc = cls._db.collection('members').document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                return {
                    "userId": data.get('userId', ''),
                    "name": data.get('name', ''),
                    "phone": data.get('phone', ''),
                    "address": data.get('address', ''),
                    "birthDate": data.get('birthDate', ''),
                    "address2": data.get('address2', '')
                }
            return None
        except Exception as e:
            logger.error(f"Error checking member: {e}")
            return None
    
    @classmethod
    def update_member(cls, user_id, name, phone, address, address2=""):
        """更新會員資料"""
        try:
            cls._db.collection('members').document(user_id).update({
                'name': name,
                'phone': phone,
                'address': address,
                'address2': address2,
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Member updated: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating member: {e}")
            return False
    
    @classmethod
    def add_order(cls, order_id, user_id, item_str, amount, status, payment_status, payment_method):
        """新增訂單"""
        try:
            now = datetime.now(TW_TZ)
            cls._db.collection('orders').document(order_id).set({
                'orderId': order_id,
                'userId': user_id,
                'items': item_str,
                'amount': amount,
                'status': status,
                'paymentStatus': payment_status,
                'paymentMethod': payment_method,
                'date': now.strftime('%Y-%m-%d %H:%M:%S'),
                'deliveryLogs': [],
                'createdAt': now,
                'updatedAt': now
            })
            logger.info(f"Order added: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return False
    
    @classmethod
    def get_user_orders(cls, user_id):
        """取得使用者訂單"""
        try:
            docs = cls._db.collection('orders').where('userId', '==', user_id).stream()
            orders = []
            for doc in docs:
                order_data = doc.to_dict()
                
                # 確保 date 字段存在且是字符串格式
                if 'date' not in order_data or order_data['date'] is None:
                    # 如果沒有 date，使用 createdAt
                    created_at = order_data.get('createdAt')
                    if created_at:
                        if hasattr(created_at, 'strftime'):
                            order_data['date'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            order_data['date'] = str(created_at)
                    else:
                        order_data['date'] = datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M:%S')
                
                # 轉換 Firestore Timestamp 為字符串
                if order_data['date'] and hasattr(order_data['date'], 'strftime'):
                    order_data['date'] = order_data['date'].strftime('%Y-%m-%d %H:%M:%S')
                
                orders.append(order_data)
            return orders
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    @classmethod
    def get_all_orders_with_members(cls):
        """取得所有訂單併入會員資料"""
        try:
            results = []
            orders_docs = cls._db.collection('orders').stream()
            
            for order_doc in orders_docs:
                order_data = order_doc.to_dict()
                user_id = order_data.get('userId')
                
                # 取得會員資料
                member_doc = cls._db.collection('members').document(user_id).get()
                customer = member_doc.to_dict() if member_doc.exists else {}
                
                # 確保 date 字段存在且是字符串格式
                if 'date' not in order_data or order_data['date'] is None:
                    # 如果沒有 date，使用 createdAt
                    created_at = order_data.get('createdAt')
                    if created_at:
                        if hasattr(created_at, 'strftime'):
                            order_data['date'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            order_data['date'] = str(created_at)
                    else:
                        order_data['date'] = datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M:%S')
                
                # 轉換 Firestore Timestamp 為字符串
                if order_data['date'] and hasattr(order_data['date'], 'strftime'):
                    order_data['date'] = order_data['date'].strftime('%Y-%m-%d %H:%M:%S')
                
                order_data['customer'] = customer
                results.append(order_data)
            
            return results
        except Exception as e:
            logger.error(f"Error getting all orders: {e}")
            return []
    
    @classmethod
    def add_delivery_log(cls, order_id, qty, address=""):
        """新增出貨紀錄"""
        try:
            order_doc = cls._db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return False, "訂單不存在"
            
            order_data = order_doc.to_dict()
            delivery_logs = order_data.get('deliveryLogs', [])
            
            # 新增日誌
            new_log = {
                "date": datetime.now(TW_TZ).isoformat(),
                "qty": qty,
                "address": address
            }
            delivery_logs.append(new_log)
            
            # 計算新狀態
            total_delivered = sum(int(log['qty']) for log in delivery_logs)
            items_str = order_data.get('items', '')
            import re
            match = re.search(r'x(\d+)', items_str)
            total_ordered = int(match.group(1)) if match else 1
            
            new_status = "已完成" if total_delivered >= total_ordered else "部分配送"
            
            # 更新訂單
            cls._db.collection('orders').document(order_id).update({
                'deliveryLogs': delivery_logs,
                'status': new_status,
                'updatedAt': datetime.now(TW_TZ)
            })
            
            logger.info(f"Delivery log added for order {order_id}")
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
    def update_order_status(cls, order_id, status):
        """更新訂單狀態"""
        try:
            cls._db.collection('orders').document(order_id).update({
                'status': status,
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Order {order_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    @classmethod
    def update_order_payment_status(cls, order_id, payment_status):
        """更新訂單付款狀態"""
        try:
            cls._db.collection('orders').document(order_id).update({
                'paymentStatus': payment_status,
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Order {order_id} payment status updated to {payment_status}")
            return True
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    @classmethod
    @classmethod
    def add_audit_log(cls, order_id, operation, admin_name, before_value, after_value, reason):
        """新增審計日誌"""
        try:
            doc_ref = cls._db.collection('auditLogs').add({
                'timestamp': datetime.now(TW_TZ).isoformat(),
                'orderId': order_id,
                'operation': operation,
                'adminName': admin_name,
                'beforeValue': before_value,
                'afterValue': after_value,
                'reason': reason
            })
            logger.info(f"Audit log added: {operation} on {order_id}")
            return True, {"orderId": order_id, "operation": operation}
        except Exception as e:
            logger.error(f"Error adding audit log: {e}")
            return False, str(e)

    
    @classmethod
    def get_delivery_audit_logs(cls, order_id):
        """取得特定訂單的審計日誌"""
        try:
            docs = cls._db.collection('auditLogs').where('orderId', '==', order_id).stream()
            logs = [doc.to_dict() for doc in docs]
            return logs
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
