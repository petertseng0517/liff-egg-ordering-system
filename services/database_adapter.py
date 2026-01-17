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
    def add_delivery_log(order_id, qty, address=""):
        """新增出貨紀錄"""
        service = DatabaseAdapter.get_service()
        return service.add_delivery_log(order_id, qty, address)
    
    # ===== 審計日誌 =====
    
    @staticmethod
    def add_audit_log(order_id, operation, admin_name, before_value, after_value, reason):
        """新增審計日誌"""
        service = DatabaseAdapter.get_service()
        return service.add_audit_log(order_id, operation, admin_name, before_value, after_value, reason)
    
    @staticmethod
    def get_delivery_audit_logs(order_id):
        """取得特定訂單的審計日誌"""
        service = DatabaseAdapter.get_service()
        return service.get_delivery_audit_logs(order_id)
