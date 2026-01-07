"""
整合測試 - Flask 應用
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

from app import app


class TestFlaskApp(unittest.TestCase):
    """Flask 應用基本測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        # 模擬 Google Sheets 初始化，避免實際連線
        with patch('services.google_sheets.GoogleSheetsService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    def test_home_route(self):
        """測試首頁路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_login_get(self):
        """測試登入頁面 GET 請求"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('後台登入'.encode('utf-8'), response.data)
    
    def test_admin_redirect_without_login(self):
        """測試未登入時訪問管理員頁面被重定向"""
        response = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
    
    def test_404_not_found(self):
        """測試 404 錯誤"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)


class TestAuthRoutes(unittest.TestCase):
    """認證路由測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        with patch('services.google_sheets.GoogleSheetsService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    def test_login_wrong_password(self):
        """測試錯誤密碼登入"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'wrong_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # 檢查是否返回登入頁面（有錯誤訊息）
        self.assertIn('登入失敗'.encode('utf-8'), response.data)
    
    def test_login_correct_password(self):
        """測試正確密碼登入"""
        with patch('config.Config.ADMIN_ACCOUNTS', {'admin': 'test_admin', 'manager': 'manager123'}):
            response = self.client.post('/login', data={
                'username': 'admin',
                'password': 'test_admin'
            }, follow_redirects=True)
            # 檢查登入是否成功（狀態碼 200）
            self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        """測試登出"""
        # 首先登入
        with patch('config.Config.ADMIN_ACCOUNTS', {'admin': 'test_admin', 'manager': 'manager123'}):
            self.client.post('/login', data={
                'username': 'admin',
                'password': 'test_admin'
            })
        
        # 然後登出
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class TestMemberAPI(unittest.TestCase):
    """會員 API 測試"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('services.google_sheets.GoogleSheetsService.check_member_exists')
    def test_check_member(self, mock_check):
        """測試成員查詢"""
        mock_check.return_value = {'userId': 'U123', 'name': 'Test'}
        
        response = self.app.post('/api/check_member', 
            json={'userId': 'U123'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    @patch('services.google_sheets.GoogleSheetsService.add_member')
    def test_add_member(self, mock_add):
        """測試新增成員"""
        mock_add.return_value = True
        
        response = self.app.post('/api/register', json={
            'userId': 'U123',
            'name': '測試',
            'phone': '0912345678',
            'address': 'Taipei'
        }, content_type='application/json')
        self.assertIn(response.status_code, [200, 201])

    @patch('services.line_service.LINEService.send_push_message')
    def test_order_notification(self, mock_line):
        """測試訂單通知"""
        mock_line.return_value = True
        
        response = self.app.post('/api/order', json={
            'userId': 'U123',
            'itemName': '土雞蛋1盤',
            'qty': 5,
            'paymentMethod': 'transfer'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        with patch('services.google_sheets.GoogleSheetsService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    @patch('services.google_sheets.GoogleSheetsService.check_member_exists')
    def test_check_member_exists(self, mock_check):
        """測試檢查會員是否存在"""
        mock_check.return_value = {
            'userId': 'U123',
            'name': 'Test User'
        }
        
        response = self.client.post('/api/check_member', 
            json={'userId': 'U123'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['registered'])
        self.assertEqual(data['name'], 'Test User')
    
    @patch('services.google_sheets.GoogleSheetsService.check_member_exists')
    def test_check_member_not_exists(self, mock_check):
        """測試會員不存在"""
        mock_check.return_value = None
        
        response = self.client.post('/api/check_member',
            json={'userId': 'U999'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['registered'])
    
    @patch('services.google_sheets.GoogleSheetsService.add_member')
    @patch('services.line_service.LINEService.send_push_message')
    def test_register_member(self, mock_line, mock_add):
        """測試註冊會員"""
        mock_add.return_value = True
        
        response = self.client.post('/api/register',
            json={
                'userId': 'U123',
                'name': 'John Doe',
                'phone': '0912345678',
                'address': 'Taipei',
                'birthDate': '1990-01-15',
                'address2': ''
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')


class TestOrderAPI(unittest.TestCase):
    """訂單 API 測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        with patch('services.google_sheets.GoogleSheetsService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    @patch('services.google_sheets.GoogleSheetsService.add_order')
    @patch('services.line_service.LINEService.send_order_confirmation')
    def test_create_order_transfer(self, mock_line, mock_add):
        """測試建立轉帳訂單"""
        mock_add.return_value = True
        
        response = self.client.post('/api/order',
            json={
                'userId': 'U123',
                'itemName': '土雞蛋1盤',
                'qty': '5',
                'remarks': 'Test order',
                'paymentMethod': 'transfer'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_create_order_invalid_item(self):
        """測試建立訂單 - 無效商品"""
        response = self.client.post('/api/order',
            json={
                'userId': 'U123',
                'itemName': '不存在的商品',
                'qty': '5',
                'paymentMethod': 'transfer'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')


if __name__ == '__main__':
    unittest.main()
