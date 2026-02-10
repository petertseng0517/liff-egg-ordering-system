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
    def get_all_members(cls):
        """獲取所有會員"""
        try:
            docs = cls._db.collection('members').stream()
            members = []
            for doc in docs:
                data = doc.to_dict()
                # 處理時間戳記
                created_at = data.get('createdAt')
                updated_at = data.get('updatedAt')
                
                if created_at and hasattr(created_at, 'strftime'):
                    data['createdAt'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    data['createdAt'] = str(created_at) if created_at else ''
                
                if updated_at and hasattr(updated_at, 'strftime'):
                    data['updatedAt'] = updated_at.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    data['updatedAt'] = str(updated_at) if updated_at else ''
                
                # 添加默認狀態如果不存在
                if 'status' not in data:
                    data['status'] = '啟用'
                
                members.append(data)
            
            # 按更新時間排序（最新優先）
            members.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)
            return members
        except Exception as e:
            logger.error(f"Error getting all members: {e}")
            return []
    
    @classmethod
    def get_member_by_id(cls, user_id):
        """按ID獲取會員資料"""
        try:
            doc = cls._db.collection('members').document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                # 處理時間戳記
                created_at = data.get('createdAt')
                updated_at = data.get('updatedAt')
                
                if created_at and hasattr(created_at, 'strftime'):
                    data['createdAt'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
                
                if updated_at and hasattr(updated_at, 'strftime'):
                    data['updatedAt'] = updated_at.strftime('%Y-%m-%d %H:%M:%S')
                
                if 'status' not in data:
                    data['status'] = '啟用'
                
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting member {user_id}: {e}")
            return None
    
    @classmethod
    def update_member_status(cls, user_id, status):
        """更新會員狀態"""
        try:
            valid_statuses = ['啟用', '停用', '黑名單']
            if status not in valid_statuses:
                return False, f"無效的狀態。必須是: {', '.join(valid_statuses)}"
            
            cls._db.collection('members').document(user_id).update({
                'status': status,
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Member status updated: {user_id} -> {status}")
            return True, "狀態更新成功"
        except Exception as e:
            logger.error(f"Error updating member status: {e}")
            return False, str(e)
    
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
                
                # 計算剩餘盤數（用於部分配送狀態）
                import re
                items_str = order_data.get('items', '')
                match = re.search(r'x(\d+)', items_str)
                total_ordered = int(match.group(1)) if match else 1
                
                delivery_logs = order_data.get('deliveryLogs', [])
                total_delivered = sum(int(log.get('qty', 0)) for log in delivery_logs)
                
                order_data['remainingQty'] = max(0, total_ordered - total_delivered)
                
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
    def add_delivery_log(cls, order_id, qty, address="", delivery_date=""):
        """新增出貨紀錄
        
        Args:
            order_id: 訂單 ID
            qty: 出貨數量
            address: 配送地點
            delivery_date: 與客戶約定的出貨日期 (YYYY-MM-DD)
        """
        try:
            order_doc = cls._db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return False, "訂單不存在"
            
            order_data = order_doc.to_dict()
            delivery_logs = order_data.get('deliveryLogs', [])
            
            # 新增日誌 - 現在包含 stamp（時間戳記）和 delivery_date（約定出貨日期）
            now = datetime.now(TW_TZ)
            new_log = {
                "stamp": now.strftime('%Y-%m-%d %H:%M:%S'),  # 系統記錄時間
                "delivery_date": delivery_date or now.strftime('%Y-%m-%d'),  # 與客戶約定的日期
                "qty": qty,
                "address": address
            }
            delivery_logs.append(new_log)
            
            # 計算新狀態（使用 corrected_qty 如果存在，否則使用 qty）
            total_delivered = sum(int(log.get('corrected_qty') or log.get('qty', 0)) for log in delivery_logs)
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
                "delivery_date": new_log.get("delivery_date", new_log.get("stamp", ""))
            }
        except Exception as e:
            logger.error(f"Error adding delivery log: {e}")
            return False, str(e)
    
    @classmethod
    def correct_delivery_log(cls, order_id, log_index, new_qty, new_address="", new_delivery_date=""):
        """修正出貨紀錄
        
        Args:
            order_id: 訂單 ID
            log_index: 出貨紀錄索引
            new_qty: 新的數量
            new_address: 新的地點
            new_delivery_date: 新的出貨日期 (YYYY-MM-DD)
        """
        try:
            order_doc = cls._db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return False, "訂單不存在"
            
            order_data = order_doc.to_dict()
            delivery_logs = order_data.get('deliveryLogs', [])
            
            if log_index < 0 or log_index >= len(delivery_logs):
                return False, "出貨紀錄不存在"
            
            # 取得修改前的數據（需取得 corrected_qty 如果存在，否則取 qty）
            old_log = delivery_logs[log_index]
            old_qty = old_log.get('corrected_qty') or old_log.get('qty', 0)
            old_address = old_log.get('address', '')
            old_delivery_date = old_log.get('delivery_date', '')
            
            # 修改出貨紀錄（保留原始 qty，新增 corrected_qty 追蹤修正後的值）
            delivery_logs[log_index] = {
                "stamp": old_log.get('stamp', old_log.get('date', datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M:%S'))),
                "delivery_date": new_delivery_date or old_delivery_date,  # 使用新日期或保留舊日期
                "date": old_log.get('date', datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M')),  # 兼容舊格式
                "qty": old_qty,  # 保留原始的預期數量
                "corrected_qty": new_qty,  # 新增修正後的實際數量
                "address": new_address,
                "original_qty": old_log.get('original_qty', old_log.get('qty', 0)),  # 記錄最初的原始值
                "is_corrected": True,
                "last_correction": datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M')
            }
            
            # 計算新狀態（使用 corrected_qty 如果存在）
            total_delivered = sum(int(log.get('corrected_qty') or log.get('qty', 0)) for log in delivery_logs)
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
            
            logger.info(f"Delivery log corrected for order {order_id}")
            return True, {
                "status": new_status,
                "old_qty": old_qty,
                "old_address": old_address,
                "new_qty": new_qty,
                "new_address": new_address,
                "old_delivery_date": old_delivery_date,
                "new_delivery_date": new_delivery_date or old_delivery_date,
                "total_delivered": total_delivered
            }
        except Exception as e:
            logger.error(f"Error correcting delivery log: {e}")
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
    
    # ===== 商品管理 =====
    
    @classmethod
    def add_product(cls, name, unit, price, cost, stock, min_stock_alert=10, max_stock_alert=1000, category_id="", supplier_id="", description="", image=""):
        """新增商品"""
        try:
            product_id = f"prod_{datetime.now(TW_TZ).strftime('%Y%m%d%H%M%S')}"
            cls._db.collection('products').document(product_id).set({
                'productId': product_id,
                'name': name,
                'description': description,
                'unit': unit,
                'price': float(price),
                'cost': float(cost),
                'stock': int(stock),
                'minStockAlert': int(min_stock_alert),
                'maxStockAlert': int(max_stock_alert),
                'categoryId': category_id,
                'supplierId': supplier_id,
                'image': image,
                'status': 'active',
                'createdAt': datetime.now(TW_TZ),
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Product added: {product_id}")
            return True, product_id
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return False, str(e)
    
    @classmethod
    def get_all_products(cls):
        """取得所有商品"""
        try:
            # 取得所有未刪除的商品（不限制狀態）
            docs = cls._db.collection('products').where('status', '!=', 'deleted').stream()
            products = []
            for doc in docs:
                product_data = doc.to_dict()
                products.append(product_data)
            logger.info(f"Retrieved {len(products)} products")
            return True, products
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return False, str(e)
    
    @classmethod
    def get_product(cls, product_id):
        """取得單一商品"""
        try:
            doc = cls._db.collection('products').document(product_id).get()
            if doc.exists:
                logger.info(f"Retrieved product: {product_id}")
                return True, doc.to_dict()
            return False, "商品不存在"
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return False, str(e)
    
    @classmethod
    def update_product(cls, product_id, **kwargs):
        """更新商品資料"""
        try:
            update_data = {
                'updatedAt': datetime.now(TW_TZ)
            }
            update_data.update(kwargs)
            cls._db.collection('products').document(product_id).update(update_data)
            logger.info(f"Product updated: {product_id}")
            return True, "商品已更新"
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return False, str(e)
    
    @classmethod
    def delete_product(cls, product_id):
        """刪除商品（軟刪除）"""
        try:
            cls._db.collection('products').document(product_id).update({
                'status': 'deleted',
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Product deleted: {product_id}")
            return True, "商品已刪除"
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False, str(e)
    
    @classmethod
    def update_product_stock(cls, product_id, qty_change, reason, operator="admin"):
        """更新商品庫存並記錄"""
        try:
            product_doc = cls._db.collection('products').document(product_id).get()
            if not product_doc.exists:
                return False, "商品不存在"
            
            product = product_doc.to_dict()
            old_stock = product.get('stock', 0)
            new_stock = old_stock + qty_change
            
            # 不允許負庫存
            if new_stock < 0:
                return False, f"庫存不足，目前庫存：{old_stock}"
            
            # 更新商品庫存
            cls._db.collection('products').document(product_id).update({
                'stock': new_stock,
                'updatedAt': datetime.now(TW_TZ)
            })
            
            # 記錄庫存異動
            cls._db.collection('stockLogs').add({
                'productId': product_id,
                'productName': product.get('name'),
                'type': 'in' if qty_change > 0 else 'out',
                'quantity': abs(qty_change),
                'oldStock': old_stock,
                'newStock': new_stock,
                'reason': reason,
                'operator': operator,
                'timestamp': datetime.now(TW_TZ).isoformat()
            })
            
            logger.info(f"Stock updated: {product_id}, change: {qty_change}")
            return True, {
                "oldStock": old_stock,
                "newStock": new_stock,
                "timestamp": datetime.now(TW_TZ).isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            return False, str(e)
    
    @classmethod
    def get_stock_logs(cls, product_id=None, limit=100):
        """取得庫存異動記錄"""
        try:
            if product_id:
                query = cls._db.collection('stockLogs').where('productId', '==', product_id)
            else:
                query = cls._db.collection('stockLogs')
            
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            logs = [doc.to_dict() for doc in docs]
            logger.info(f"Retrieved {len(logs)} stock logs")
            return True, logs
        except Exception as e:
            logger.error(f"Error getting stock logs: {e}")
            return False, str(e)
    
    @classmethod
    def get_low_stock_products(cls):
        """取得庫存不足的商品"""
        try:
            # 取得所有未刪除的商品
            docs = cls._db.collection('products').where('status', '!=', 'deleted').stream()
            low_stock = []
            for doc in docs:
                product = doc.to_dict()
                if product.get('stock', 0) <= product.get('minStockAlert', 10):
                    low_stock.append(product)
            logger.info(f"Retrieved {len(low_stock)} low stock products")
            return True, low_stock
        except Exception as e:
            logger.error(f"Error getting low stock products: {e}")
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
    # ===== 分類管理 =====
    @classmethod
    def add_category(cls, name, description="", color="", icon=""):
        """新增分類"""
        try:
            doc_ref = cls._db.collection('categories').add({
                'name': name,
                'description': description,
                'color': color,
                'icon': icon,
                'status': 'active',
                'createdAt': datetime.now(TW_TZ),
                'updatedAt': datetime.now(TW_TZ)
            })
            category_id = doc_ref[1].id
            logger.info(f"Category added: {category_id}")
            return True, category_id
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return False, str(e)
    
    @classmethod
    def get_all_categories(cls):
        """取得所有分類"""
        try:
            docs = cls._db.collection('categories').where('status', '!=', 'deleted').stream()
            categories = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            logger.info(f"Retrieved {len(categories)} categories")
            return True, categories
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return False, str(e)
    
    @classmethod
    def get_category(cls, category_id):
        """取得單一分類"""
        try:
            doc = cls._db.collection('categories').document(category_id).get()
            if not doc.exists:
                return False, "分類不存在"
            return True, {'id': doc.id, **doc.to_dict()}
        except Exception as e:
            logger.error(f"Error getting category: {e}")
            return False, str(e)
    
    @classmethod
    def update_category(cls, category_id, **kwargs):
        """更新分類"""
        try:
            kwargs['updatedAt'] = datetime.now(TW_TZ)
            cls._db.collection('categories').document(category_id).update(kwargs)
            logger.info(f"Category updated: {category_id}")
            return True, "分類已更新"
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            return False, str(e)
    
    @classmethod
    def delete_category(cls, category_id):
        """刪除分類 (軟刪除)"""
        try:
            cls._db.collection('categories').document(category_id).update({
                'status': 'deleted',
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Category deleted: {category_id}")
            return True, "分類已刪除"
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False, str(e)

    # ===== 折扣管理 =====
    @classmethod
    def add_discount(cls, name, discount_type, discount_value, target_type="product", 
                     target_id=None, start_date=None, end_date=None, description=""):
        """
        新增折扣
        discount_type: 'fixed' (固定金額) 或 'percentage' (百分比)
        target_type: 'product', 'category', 'member_level'
        """
        try:
            doc_ref = cls._db.collection('discounts').add({
                'name': name,
                'discountType': discount_type,
                'discountValue': discount_value,
                'targetType': target_type,
                'targetId': target_id,
                'startDate': start_date,
                'endDate': end_date,
                'description': description,
                'status': 'active',
                'createdAt': datetime.now(TW_TZ),
                'updatedAt': datetime.now(TW_TZ)
            })
            discount_id = doc_ref[1].id
            logger.info(f"Discount added: {discount_id}")
            return True, discount_id
        except Exception as e:
            logger.error(f"Error adding discount: {e}")
            return False, str(e)
    
    @classmethod
    def get_all_discounts(cls):
        """取得所有折扣"""
        try:
            docs = cls._db.collection('discounts').where('status', '!=', 'deleted').stream()
            discounts = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            logger.info(f"Retrieved {len(discounts)} discounts")
            return True, discounts
        except Exception as e:
            logger.error(f"Error getting discounts: {e}")
            return False, str(e)
    
    @classmethod
    def get_discount(cls, discount_id):
        """取得單一折扣"""
        try:
            doc = cls._db.collection('discounts').document(discount_id).get()
            if not doc.exists:
                return False, "折扣不存在"
            return True, {'id': doc.id, **doc.to_dict()}
        except Exception as e:
            logger.error(f"Error getting discount: {e}")
            return False, str(e)
    
    @classmethod
    def update_discount(cls, discount_id, **kwargs):
        """更新折扣"""
        try:
            kwargs['updatedAt'] = datetime.now(TW_TZ)
            cls._db.collection('discounts').document(discount_id).update(kwargs)
            logger.info(f"Discount updated: {discount_id}")
            return True, "折扣已更新"
        except Exception as e:
            logger.error(f"Error updating discount: {e}")
            return False, str(e)
    
    @classmethod
    def delete_discount(cls, discount_id):
        """刪除折扣 (軟刪除)"""
        try:
            cls._db.collection('discounts').document(discount_id).update({
                'status': 'deleted',
                'updatedAt': datetime.now(TW_TZ)
            })
            logger.info(f"Discount deleted: {discount_id}")
            return True, "折扣已刪除"
        except Exception as e:
            logger.error(f"Error deleting discount: {e}")
            return False, str(e)
    
    @classmethod
    def get_applicable_discounts(cls, product_id, category_id=None, member_level=None):
        """取得適用的折扣"""
        try:
            discounts = []
            now = datetime.now(TW_TZ)
            
            # 查詢商品折扣
            docs = cls._db.collection('discounts') \
                .where('status', '==', 'active') \
                .where('targetType', '==', 'product') \
                .where('targetId', '==', product_id).stream()
            
            for doc in docs:
                discount = doc.to_dict()
                # 檢查時間範圍
                if discount.get('startDate') and discount.get('endDate'):
                    start = datetime.fromisoformat(discount['startDate']) if isinstance(discount['startDate'], str) else discount['startDate']
                    end = datetime.fromisoformat(discount['endDate']) if isinstance(discount['endDate'], str) else discount['endDate']
                    if start <= now <= end:
                        discounts.append({'id': doc.id, **discount})
                else:
                    discounts.append({'id': doc.id, **discount})
            
            # 查詢分類折扣
            if category_id:
                docs = cls._db.collection('discounts') \
                    .where('status', '==', 'active') \
                    .where('targetType', '==', 'category') \
                    .where('targetId', '==', category_id).stream()
                
                for doc in docs:
                    discount = doc.to_dict()
                    if discount.get('startDate') and discount.get('endDate'):
                        start = datetime.fromisoformat(discount['startDate']) if isinstance(discount['startDate'], str) else discount['startDate']
                        end = datetime.fromisoformat(discount['endDate']) if isinstance(discount['endDate'], str) else discount['endDate']
                        if start <= now <= end:
                            discounts.append({'id': doc.id, **discount})
                    else:
                        discounts.append({'id': doc.id, **discount})
            
            return True, discounts
        except Exception as e:
            logger.error(f"Error getting applicable discounts: {e}")
            return False, str(e)

    # ===== 庫存警告 =====
    @classmethod
    def add_stock_alert(cls, product_id, alert_type, threshold, operator="system"):
        """
        新增庫存警告
        alert_type: 'critical' (超低), 'low' (低於), 'high' (超過)
        """
        try:
            cls._db.collection('stockAlerts').add({
                'productId': product_id,
                'alertType': alert_type,
                'threshold': threshold,
                'status': 'active',
                'operator': operator,
                'createdAt': datetime.now(TW_TZ),
                'acknowledgedAt': None,
                'acknowledgedBy': None
            })
            logger.info(f"Stock alert added: {product_id} - {alert_type}")
            return True, "警告已記錄"
        except Exception as e:
            logger.error(f"Error adding stock alert: {e}")
            return False, str(e)
    
    @classmethod
    def get_stock_alerts(cls, status='active', alert_type=None):
        """取得庫存警告"""
        try:
            # 簡化查詢，避免複合索引需求
            docs = cls._db.collection('stockAlerts').stream()
            alerts = []
            
            for doc in docs:
                alert = doc.to_dict()
                # 在記憶體中進行篩選
                if alert.get('status') == status:
                    if not alert_type or alert.get('alertType') == alert_type:
                        alerts.append({'id': doc.id, **alert})
            
            # 按 createdAt 倒序排列
            alerts.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            
            logger.info(f"Retrieved {len(alerts)} stock alerts")
            return True, alerts
        except Exception as e:
            logger.error(f"Error getting stock alerts: {e}")
            return False, str(e)
    
    @classmethod
    def acknowledge_stock_alert(cls, alert_id, acknowledged_by="admin"):
        """確認庫存警告"""
        try:
            cls._db.collection('stockAlerts').document(alert_id).update({
                'status': 'acknowledged',
                'acknowledgedAt': datetime.now(TW_TZ),
                'acknowledgedBy': acknowledged_by
            })
            logger.info(f"Stock alert acknowledged: {alert_id}")
            return True, "警告已確認"
        except Exception as e:
            logger.error(f"Error acknowledging stock alert: {e}")
            return False, str(e)
    
    @classmethod
    def check_and_create_stock_alerts(cls, product_id):
        """檢查並創建庫存警告"""
        try:
            product_doc = cls._db.collection('products').document(product_id).get()
            if not product_doc.exists:
                return False, "商品不存在"
            
            product = product_doc.to_dict()
            stock = product.get('stock', 0)
            min_stock_alert = product.get('minStockAlert', 10)
            max_stock_alert = product.get('maxStockAlert', 1000)
            
            # 檢查超低庫存 (低於最低值的 30%)
            critical_level = min_stock_alert * 0.3
            if stock < critical_level:
                cls.add_stock_alert(product_id, 'critical', critical_level)
            
            # 檢查低庫存
            if stock <= min_stock_alert:
                cls.add_stock_alert(product_id, 'low', min_stock_alert)
            
            # 檢查超過上限
            if stock > max_stock_alert:
                cls.add_stock_alert(product_id, 'high', max_stock_alert)
            
            return True, "警告檢查完成"
        except Exception as e:
            logger.error(f"Error checking stock alerts: {e}")
            return False, str(e)