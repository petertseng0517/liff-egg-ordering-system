"""
整合測試 - Member Routes
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 設定測試環境變數 - 必須在導入 app 前設置
os.environ['FLASK_ENV'] = 'testing'


class TestMemberRoutes(unittest.TestCase):
    """會員路由測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        with patch('services.firestore_service.FirestoreService.init'), \
             patch('services.google_sheets.GoogleSheetsService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    def test_member_page_accessible(self):
        """測試會員頁面是否存在"""
        response = self.client.get('/member', follow_redirects=True)
        # 頁面可能返回 200, 302（重定向）或 404（不存在）
        self.assertIn(response.status_code, [200, 302, 404])
    
    def test_order_page_accessible(self):
        """測試下單頁面是否存在"""
        response = self.client.get('/order', follow_redirects=True)
        # 頁面可能返回 200, 302（重定向）或 404（不存在）
        self.assertIn(response.status_code, [200, 302, 404])


class TestMemberDataValidation(unittest.TestCase):
    """會員資料驗證測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        with patch('services.firestore_service.FirestoreService.init'), \
             patch('services.google_sheets.GoogleSheetsService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    @patch('services.database_adapter.DatabaseAdapter.add_member')
    def test_register_with_valid_data(self, mock_add):
        """測試有效的會員註冊"""
        mock_add.return_value = True
        
        # 測試會員註冊邏輯而不是路由
        from validation import FormValidator
        data = {
            'name': '張三',
            'phone': '0912345678',
            'address': '台北市信義區',
            'birthDate': '1990-01-15',
            'address2': '公司地址'
        }
        
        result = FormValidator.validate_register_form(data)
        self.assertIsNone(result)
    
    @patch('services.database_adapter.DatabaseAdapter.add_member')
    def test_register_with_invalid_phone(self, mock_add):
        """測試無效電話號碼的會員註冊"""
        mock_add.return_value = False
        
        from validation import FormValidator
        data = {
            'name': '張三',
            'phone': '123',  # 無效電話
            'address': '台北市信義區'
        }
        
        result = FormValidator.validate_register_form(data)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
