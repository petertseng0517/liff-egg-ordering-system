"""
單元測試 - LINE Messaging Service
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.line_service import LINEService


class TestLINEService(unittest.TestCase):
    """LINE 訊息服務測試"""
    
    def setUp(self):
        """測試前設置"""
        self.user_id = "U1234567890abcdef1234567890abcdef"
        self.order_id = "ORD-2026-001"
    
    @patch('services.line_service.Config')
    def test_send_push_message_success(self, mock_config):
        """測試成功推送訊息"""
        mock_config.LINE_CHANNEL_ACCESS_TOKEN = "test_token"
        
        with patch('services.line_service.ApiClient') as mock_api_client, \
             patch('services.line_service.MessagingApi') as mock_messaging_api:
            
            mock_instance = MagicMock()
            mock_api_client.return_value.__enter__.return_value = mock_instance
            
            result = LINEService.send_push_message(self.user_id, "Test message")
            self.assertTrue(result)
    
    @patch('services.line_service.Config')
    def test_send_push_message_no_token(self, mock_config):
        """測試未配置 token 時"""
        mock_config.LINE_CHANNEL_ACCESS_TOKEN = None
        
        result = LINEService.send_push_message(self.user_id, "Test message")
        self.assertFalse(result)
    
    @patch('services.line_service.Config')
    def test_send_push_message_empty_user_id(self, mock_config):
        """測試空的用戶 ID"""
        mock_config.LINE_CHANNEL_ACCESS_TOKEN = "test_token"
        
        result = LINEService.send_push_message("", "Test message")
        self.assertFalse(result)
    
    @patch('services.line_service.Config')
    def test_send_push_message_error(self, mock_config):
        """測試推送訊息發生錯誤"""
        mock_config.LINE_CHANNEL_ACCESS_TOKEN = "test_token"
        
        with patch('services.line_service.ApiClient') as mock_api_client:
            mock_api_client.return_value.__enter__.side_effect = Exception("API Error")
            
            result = LINEService.send_push_message(self.user_id, "Test message")
            self.assertFalse(result)
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_order_confirmation(self, mock_send):
        """測試發送訂單確認訊息"""
        mock_send.return_value = True
        
        result = LINEService.send_order_confirmation(
            self.user_id,
            self.order_id,
            "土雞蛋 5盤",
            1250,
            "未付款"
        )
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        # 驗證訊息內容包含關鍵資訊
        call_args = mock_send.call_args
        self.assertIn(self.order_id, call_args[0][1])
        self.assertIn("土雞蛋 5盤", call_args[0][1])
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_payment_success(self, mock_send):
        """測試發送付款成功訊息"""
        mock_send.return_value = True
        
        result = LINEService.send_payment_success(self.user_id, self.order_id)
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertIn(self.order_id, call_args[0][1])
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_delivery_notification(self, mock_send):
        """測試發送出貨通知訊息"""
        mock_send.return_value = True
        delivery_date = "2026-01-20"
        qty = 5
        remaining_qty = 0
        
        result = LINEService.send_delivery_notification(
            self.user_id,
            self.order_id,
            delivery_date,
            qty,
            remaining_qty
        )
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertIn(self.order_id, call_args[0][1])
        self.assertIn(delivery_date, call_args[0][1])
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_delivery_correction_notification(self, mock_send):
        """測試發送出貨紀錄修正通知訊息"""
        mock_send.return_value = True
        
        result = LINEService.send_delivery_correction_notification(
            self.user_id,
            self.order_id,
            "2026-01-20",
            5,
            4
        )
        
        self.assertTrue(result)
        mock_send.assert_called_once()
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_status_update(self, mock_send):
        """測試發送狀態更新訊息"""
        mock_send.return_value = True
        
        result = LINEService.send_status_update(self.user_id, self.order_id, "已配送")
        
        self.assertTrue(result)
        mock_send.assert_called_once()


if __name__ == '__main__':
    unittest.main()
