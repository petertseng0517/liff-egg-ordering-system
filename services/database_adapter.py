"""
資料庫適配器 - 支援 Google Sheets 和 Firestore 切換
"""
from config import Config
from services.google_sheets import GoogleSheetsService
from services.firestore_service import FirestoreService
import logging

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """資料庫適配器 - 統一介面支援多個後端"""
    
    @staticmethod
    def get_service():
        """根據配置返回相應的服務"""
        if Config.USE_FIRESTORE:
            return FirestoreService
        else:
            return GoogleSheetsService
    
    # ===== 會員相關操作 =====
    
    @staticmethod
    def add_member(user_id, name, phone, address, birth_date=None, address2=None):
        """新增會員"""
        service = DatabaseAdapter.get_service()
        return service.add_member(user_id, name, phone, address, birth_date, address2)
    
    @staticmethod
    def check_member_exists(user_id):
        """檢查會員是否存在"""
        service = DatabaseAdapter.get_service()
        return service.check_member_exists(user_id)
    
    @staticmethod
    def update_member(user_id, name, phone, address, address2=""):
        """更新會員資料"""
        service = DatabaseAdapter.get_service()
        return service.update_member(user_id, name, phone, address, address2)
    
    @staticmethod
    def get_all_members():
        """獲取所有會員"""
        service = DatabaseAdapter.get_service()
        return service.get_all_members()
    
    @staticmethod
    def get_member_by_id(user_id):
        """按ID獲取會員資料"""
        service = DatabaseAdapter.get_service()
        return service.get_member_by_id(user_id)
    
    @staticmethod
    def update_member_status(user_id, status):
        """更新會員狀態"""
        service = DatabaseAdapter.get_service()
        return service.update_member_status(user_id, status)
    
    # ===== 訂單相關操作 =====
    
    @staticmethod
    def add_order(order_id, user_id, item_str, amount, status, payment_status, payment_method):
        """新增訂單"""
        service = DatabaseAdapter.get_service()
        return service.add_order(order_id, user_id, item_str, amount, status, payment_status, payment_method)
    
    @staticmethod
    def get_user_orders(user_id):
        """取得使用者訂單"""
        service = DatabaseAdapter.get_service()
        return service.get_user_orders(user_id)
    
    @staticmethod
    def get_all_orders_with_members():
        """取得所有訂單併入會員資料"""
        service = DatabaseAdapter.get_service()
        return service.get_all_orders_with_members()
    
    @staticmethod
    def update_order_status(order_id, status):
        """更新訂單狀態"""
        service = DatabaseAdapter.get_service()
        return service.update_order_status(order_id, status)
    
    @staticmethod
    def update_order_payment_status(order_id, payment_status):
        """更新訂單付款狀態"""
        service = DatabaseAdapter.get_service()
        return service.update_order_payment_status(order_id, payment_status)
    
    # ===== 出貨相關操作 =====
    
    @staticmethod
    def add_delivery_log(order_id, qty, address="", delivery_date=""):
        """新增出貨紀錄"""
        service = DatabaseAdapter.get_service()
        return service.add_delivery_log(order_id, qty, address, delivery_date)
    
    @staticmethod
    def correct_delivery_log(order_id, log_index, new_qty, new_address="", new_delivery_date=""):
        """修正出貨紀錄"""
        service = DatabaseAdapter.get_service()
        return service.correct_delivery_log(order_id, log_index, new_qty, new_address, new_delivery_date)
    
    # ===== 審計日誌 =====
    
    @staticmethod
    def add_audit_log(order_id, operation, admin_name, before_value, after_value, reason):
        """新增審計日誌"""
        service = DatabaseAdapter.get_service()
        return service.add_audit_log(order_id, operation, admin_name, before_value, after_value, reason)
    
    # 商品管理方法
    @staticmethod
    def add_product(name, unit, price, cost, stock, min_stock_alert, category_id=None, supplier_id=None, description=None, image=None):
        """新增商品"""
        service = DatabaseAdapter.get_service()
        return service.add_product(
            name=name,
            unit=unit,
            price=price,
            cost=cost,
            stock=stock,
            min_stock_alert=min_stock_alert,
            category_id=category_id or '',
            supplier_id=supplier_id or '',
            description=description or '',
            image=image or ''
        )
    
    @staticmethod
    def get_all_products():
        """取得所有商品"""
        service = DatabaseAdapter.get_service()
        return service.get_all_products()
    
    @staticmethod
    def get_product(product_id):
        """取得特定商品"""
        service = DatabaseAdapter.get_service()
        return service.get_product(product_id)
    
    @staticmethod
    def update_product(product_id, **kwargs):
        """更新商品資訊"""
        service = DatabaseAdapter.get_service()
        return service.update_product(product_id, **kwargs)
    
    @staticmethod
    def delete_product(product_id):
        """刪除商品（軟刪除）"""
        service = DatabaseAdapter.get_service()
        return service.delete_product(product_id)
    
    @staticmethod
    def update_product_stock(product_id, qty_change, reason, operator):
        """更新商品庫存"""
        service = DatabaseAdapter.get_service()
        return service.update_product_stock(product_id, qty_change, reason, operator)
    
    @staticmethod
    def get_stock_logs(product_id=None, limit=100):
        """取得庫存日誌"""
        service = DatabaseAdapter.get_service()
        return service.get_stock_logs(product_id, limit)
    
    @staticmethod
    def get_low_stock_products():
        """取得低庫存商品"""
        service = DatabaseAdapter.get_service()
        return service.get_low_stock_products()
    
    @staticmethod
    def get_delivery_audit_logs(order_id):
        """取得特定訂單的審計日誌"""
        service = DatabaseAdapter.get_service()
        return service.get_delivery_audit_logs(order_id)
    # ===== 分類管理 =====
    @staticmethod
    def add_category(name, description="", color="", icon=""):
        """新增分類"""
        service = DatabaseAdapter.get_service()
        return service.add_category(name, description, color, icon)
    
    @staticmethod
    def get_all_categories():
        """取得所有分類"""
        service = DatabaseAdapter.get_service()
        return service.get_all_categories()
    
    @staticmethod
    def get_category(category_id):
        """取得單一分類"""
        service = DatabaseAdapter.get_service()
        return service.get_category(category_id)
    
    @staticmethod
    def update_category(category_id, **kwargs):
        """更新分類"""
        service = DatabaseAdapter.get_service()
        return service.update_category(category_id, **kwargs)
    
    @staticmethod
    def delete_category(category_id):
        """刪除分類"""
        service = DatabaseAdapter.get_service()
        return service.delete_category(category_id)

    # ===== 折扣管理 =====
    @staticmethod
    def add_discount(name, discount_type, discount_value, target_type="product", 
                     target_id=None, start_date=None, end_date=None, description=""):
        """新增折扣"""
        service = DatabaseAdapter.get_service()
        return service.add_discount(name, discount_type, discount_value, target_type, 
                                   target_id, start_date, end_date, description)
    
    @staticmethod
    def get_all_discounts():
        """取得所有折扣"""
        service = DatabaseAdapter.get_service()
        return service.get_all_discounts()
    
    @staticmethod
    def get_discount(discount_id):
        """取得單一折扣"""
        service = DatabaseAdapter.get_service()
        return service.get_discount(discount_id)
    
    @staticmethod
    def update_discount(discount_id, **kwargs):
        """更新折扣"""
        service = DatabaseAdapter.get_service()
        return service.update_discount(discount_id, **kwargs)
    
    @staticmethod
    def delete_discount(discount_id):
        """刪除折扣"""
        service = DatabaseAdapter.get_service()
        return service.delete_discount(discount_id)
    
    @staticmethod
    def get_applicable_discounts(product_id, category_id=None, member_level=None):
        """取得適用的折扣"""
        service = DatabaseAdapter.get_service()
        return service.get_applicable_discounts(product_id, category_id, member_level)

    # ===== 庫存警告 =====
    @staticmethod
    def add_stock_alert(product_id, alert_type, threshold, operator="system"):
        """新增庫存警告"""
        service = DatabaseAdapter.get_service()
        return service.add_stock_alert(product_id, alert_type, threshold, operator)
    
    @staticmethod
    def get_stock_alerts(status='active', alert_type=None):
        """取得庫存警告"""
        service = DatabaseAdapter.get_service()
        return service.get_stock_alerts(status, alert_type)
    
    @staticmethod
    def acknowledge_stock_alert(alert_id, acknowledged_by="admin"):
        """確認庫存警告"""
        service = DatabaseAdapter.get_service()
        return service.acknowledge_stock_alert(alert_id, acknowledged_by)
    
    @staticmethod
    def check_and_create_stock_alerts(product_id):
        """檢查並創建庫存警告"""
        service = DatabaseAdapter.get_service()
        return service.check_and_create_stock_alerts(product_id)