"""
單元測試 - Firebase Firestore Service
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.firestore_service import FirestoreService


class TestFirestoreService(unittest.TestCase):
    """Firebase Firestore 服務測試"""
    
    def setUp(self):
        """測試前設置"""
        self.user_id = "user123"
        self.order_id = "ORD-2026-001"
        self.member_data = {
            'userId': self.user_id,
            'name': '張三',
            'phone': '0912345678',
            'address': '台北市信義區',
            'birthDate': '1990-01-15',
            'address2': '公司地址'
        }
    
    @patch('services.firestore_service.firebase_admin')
    @patch('services.firestore_service.credentials')
    @patch('services.firestore_service.firestore')
    def test_init_success(self, mock_fs, mock_creds, mock_admin):
        """測試初始化成功"""
        mock_admin._apps = []
        mock_fs.client.return_value = MagicMock()
        
        # 模擬 Firebase 初始化
        FirestoreService.init()
        
        # 驗證 Firebase 初始化被調用
        self.assertIsNotNone(FirestoreService._db)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_add_member_success(self, mock_db):
        """測試成功新增會員"""
        FirestoreService._db = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        result = FirestoreService.add_member(
            self.user_id,
            '張三',
            '0912345678',
            '台北市信義區',
            '1990-01-15',
            '公司地址'
        )
        
        self.assertTrue(result)
        mock_collection.document.assert_called_with(self.user_id)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_add_member_error(self, mock_db):
        """測試新增會員發生錯誤"""
        FirestoreService._db = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_collection.document.side_effect = Exception("Database error")
        
        result = FirestoreService.add_member(
            self.user_id,
            '張三',
            '0912345678',
            '台北市信義區'
        )
        
        self.assertFalse(result)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_check_member_exists_true(self, mock_db):
        """測試會員存在"""
        FirestoreService._db = mock_db
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = self.member_data
        
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value.get.return_value = mock_doc
        
        result = FirestoreService.check_member_exists(self.user_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['userId'], self.user_id)
        self.assertEqual(result['name'], '張三')
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_check_member_exists_false(self, mock_db):
        """測試會員不存在"""
        FirestoreService._db = mock_db
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value.get.return_value = mock_doc
        
        result = FirestoreService.check_member_exists(self.user_id)
        
        self.assertIsNone(result)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_update_member_success(self, mock_db):
        """測試成功更新會員"""
        FirestoreService._db = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        result = FirestoreService.update_member(
            self.user_id,
            '李四',
            '0987654321',
            '台中市中心',
            '辦公室'
        )
        
        self.assertTrue(result)
        mock_collection.document.assert_called_with(self.user_id)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_add_order_success(self, mock_db):
        """測試成功新增訂單"""
        FirestoreService._db = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        result = FirestoreService.add_order(
            self.order_id,
            self.user_id,
            '土雞蛋 5盤',
            1250,
            '待配送',
            '已付款',
            'ecpay'
        )
        
        self.assertTrue(result)
        mock_collection.document.assert_called_with(self.order_id)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_get_user_orders_success(self, mock_db):
        """測試取得用戶訂單"""
        FirestoreService._db = mock_db
        order_data = {
            'orderId': self.order_id,
            'userId': self.user_id,
            'itemStr': '土雞蛋 5盤',
            'amount': 1250,
            'status': '待配送'
        }
        
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = order_data
        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        
        result = FirestoreService.get_user_orders(self.user_id)
        
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_update_order_status_success(self, mock_db):
        """測試更新訂單狀態"""
        FirestoreService._db = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        result = FirestoreService.update_order_status(self.order_id, '已配送')
        
        self.assertTrue(result)
        mock_collection.document.assert_called_with(self.order_id)
    
    @patch('services.firestore_service.FirestoreService._db')
    def test_add_delivery_log_success(self, mock_db):
        """測試新增配送紀錄"""
        FirestoreService._db = mock_db
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        result = FirestoreService.add_delivery_log(
            self.order_id,
            5,
            '台北市信義區 XXX號'
        )
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
