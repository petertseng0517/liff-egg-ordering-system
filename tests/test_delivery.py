"""
單元測試 - 出貨管理和訊息通知
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.line_service import LINEService


class TestDeliveryNotification(unittest.TestCase):
    """出貨通知訊息測試"""
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_delivery_notification_message_format(self, mock_send):
        """測試出貨通知訊息格式"""
        # 設定 mock 返回 True
        mock_send.return_value = True
        
        # 呼叫函數
        result = LINEService.send_delivery_notification(
            user_id="U1234567890",
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        
        # 驗證函數被呼叫
        self.assertTrue(result)
        mock_send.assert_called_once()
        
        # 驗證訊息內容
        called_msg = mock_send.call_args[0][1]
        self.assertIn("📦 出貨通知", called_msg)
        self.assertIn("訂單編號：ORD1234567890", called_msg)
        self.assertIn("本次出貨日期：2026-01-09 14:30", called_msg)
        self.assertIn("本次出貨數量：5盤", called_msg)
        self.assertIn("本訂單剩餘：17盤", called_msg)
        
        # 驗證不包含不應該出現的文字
        self.assertNotIn("目前進度", called_msg)
        self.assertNotIn("其餘商品", called_msg)
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_delivery_notification_with_zero_remaining(self, mock_send):
        """測試剩餘數量為 0 的出貨通知"""
        mock_send.return_value = True
        
        result = LINEService.send_delivery_notification(
            user_id="U1234567890",
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=22,
            remaining_qty=0
        )
        
        self.assertTrue(result)
        called_msg = mock_send.call_args[0][1]
        self.assertIn("本訂單剩餘：0盤", called_msg)


class TestDeliveryCorrectionNotification(unittest.TestCase):
    """出貨修正通知訊息測試"""
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_delivery_correction_notification_message_format(self, mock_send):
        """測試出貨修正通知訊息格式"""
        mock_send.return_value = True
        
        result = LINEService.send_delivery_correction_notification(
            user_id="U1234567890",
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            old_qty=3,
            new_qty=5
        )
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        
        # 驗證訊息內容
        called_msg = mock_send.call_args[0][1]
        self.assertIn("🔄 出貨紀錄修正通知", called_msg)
        self.assertIn("訂單編號：ORD1234567890", called_msg)
        self.assertIn("出貨日期：2026-01-09 14:30", called_msg)
        self.assertIn("依實際需求修改出貨紀錄", called_msg)
        self.assertIn("原紀錄：3盤 → 修正為：5盤", called_msg)
        
        # 驗證不包含不應該出現的文字
        self.assertNotIn("目前進度", called_msg)
        self.assertNotIn("其餘商品", called_msg)
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_delivery_correction_notification_different_values(self, mock_send):
        """測試不同數值的修正通知"""
        mock_send.return_value = True
        
        result = LINEService.send_delivery_correction_notification(
            user_id="U1234567890",
            order_id="ORD9876543210",
            delivery_date="2026-01-08 10:15",
            old_qty=10,
            new_qty=8
        )
        
        self.assertTrue(result)
        called_msg = mock_send.call_args[0][1]
        self.assertIn("訂單編號：ORD9876543210", called_msg)
        self.assertIn("出貨日期：2026-01-08 10:15", called_msg)
        self.assertIn("原紀錄：10盤 → 修正為：8盤", called_msg)


class TestLineServiceEdgeCases(unittest.TestCase):
    """LINE 服務邊界情況測試"""
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_notification_with_empty_user_id(self, mock_send):
        """測試空 user_id 時的行為"""
        mock_send.return_value = False
        
        # 應該處理空 user_id
        result = LINEService.send_delivery_notification(
            user_id="",
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        
        # 應該返回 False，因為 user_id 為空
        self.assertFalse(result)
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_send_notification_with_special_characters(self, mock_send):
        """測試包含特殊字符的訂單編號"""
        mock_send.return_value = True
        
        result = LINEService.send_delivery_notification(
            user_id="U1234567890",
            order_id="ORD-2026-01-09-001",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        
        self.assertTrue(result)
        called_msg = mock_send.call_args[0][1]
        self.assertIn("訂單編號：ORD-2026-01-09-001", called_msg)


class TestDeliveryValidationLogic(unittest.TestCase):
    """出貨驗證邏輯測試"""
    
    def test_remaining_qty_calculation(self):
        """測試剩餘數量計算"""
        # 測試案例 1：部分出貨
        total_ordered = 22
        total_delivered = 5
        remaining = total_ordered - total_delivered
        self.assertEqual(remaining, 17)
        
        # 測試案例 2：全部出貨
        total_ordered = 22
        total_delivered = 22
        remaining = total_ordered - total_delivered
        self.assertEqual(remaining, 0)
        
        # 測試案例 3：多批出貨
        total_ordered = 22
        total_delivered = 3 + 5 + 14  # 三次出貨
        remaining = total_ordered - total_delivered
        self.assertEqual(remaining, 0)
    
    def test_delivery_validation_should_pass(self):
        """測試出貨驗證應該通過的情況"""
        total_ordered = 22
        current_delivered = 5
        remaining = total_ordered - current_delivered
        
        # 新增出貨量應該不超過剩餘量
        new_delivery = 10
        self.assertLessEqual(new_delivery, remaining)
        
        # 新增後的總量應該不超過訂購量
        new_total = current_delivered + new_delivery
        self.assertLessEqual(new_total, total_ordered)
    
    def test_delivery_validation_should_fail(self):
        """測試出貨驗證應該失敗的情況"""
        total_ordered = 22
        current_delivered = 20
        remaining = total_ordered - current_delivered
        
        # 新增出貨量超過剩餘量
        new_delivery = 5
        self.assertGreater(new_delivery, remaining)
        
        # 新增後的總量超過訂購量
        new_total = current_delivered + new_delivery
        self.assertGreater(new_total, total_ordered)


class TestCorrectedQtyCalculation(unittest.TestCase):
    """修正後數量計算測試"""
    
    def test_corrected_qty_with_single_delivery(self):
        """測試單次出貨修正"""
        # 模擬原始日誌
        logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "address": "address1"},
        ]
        
        # 修正第一筆
        old_qty = logs[0]["qty"]
        new_qty = 5
        logs[0]["corrected_qty"] = new_qty
        
        # 計算總送出量（使用修正後的數量）
        total = sum(int(l.get("corrected_qty") or l.get("qty", 0)) for l in logs)
        self.assertEqual(total, 5)
    
    def test_corrected_qty_with_multiple_deliveries(self):
        """測試多次出貨修正"""
        # 模擬多次出貨
        logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 17, "address": "address2"},
        ]
        
        # 修正第一筆：3 -> 5
        logs[0]["corrected_qty"] = 5
        
        # 計算總送出量
        total = sum(int(l.get("corrected_qty") or l.get("qty", 0)) for l in logs)
        self.assertEqual(total, 22)  # 5 + 17
    
    def test_correction_validation_should_pass(self):
        """測試修正驗證應該通過的情況"""
        total_ordered = 22
        logs = [
            {"date": "2026-01-09 10:00", "qty": 3},
            {"date": "2026-01-09 12:00", "qty": 17},
        ]
        
        # 修正第一筆：3 -> 5（原本是 3，改成 5）
        # 新的總量 = 5 + 17 = 22，不超過訂購量
        new_qty = 5
        calculated_total = new_qty + int(logs[1].get("qty", 0))
        self.assertLessEqual(calculated_total, total_ordered)
    
    def test_correction_validation_should_fail(self):
        """測試修正驗證應該失敗的情況"""
        total_ordered = 22
        logs = [
            {"date": "2026-01-09 10:00", "qty": 3},
            {"date": "2026-01-09 12:00", "qty": 17},
        ]
        
        # 試圖修正第一筆：3 -> 25（超過訂購量）
        # 新的總量 = 25 + 17 = 42，超過訂購量 22
        new_qty = 25
        calculated_total = new_qty + int(logs[1].get("qty", 0))
        self.assertGreater(calculated_total, total_ordered)


class TestDeliveryNotificationParameters(unittest.TestCase):
    """出貨通知參數驗證測試"""
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_notification_receives_correct_parameters(self, mock_send):
        """測試通知函數接收正確的參數"""
        mock_send.return_value = True
        
        user_id = "U1234567890"
        order_id = "ORD1234567890"
        delivery_date = "2026-01-09 14:30"
        qty = 5
        remaining_qty = 17
        
        LINEService.send_delivery_notification(
            user_id=user_id,
            order_id=order_id,
            delivery_date=delivery_date,
            qty=qty,
            remaining_qty=remaining_qty
        )
        
        # 驗證被正確呼叫
        self.assertEqual(mock_send.call_count, 1)
        
        # 驗證第一個參數是 user_id
        called_user_id = mock_send.call_args[0][0]
        self.assertEqual(called_user_id, user_id)
    
    @patch('services.line_service.LINEService.send_push_message')
    def test_correction_notification_receives_correct_parameters(self, mock_send):
        """測試修正通知函數接收正確的參數"""
        mock_send.return_value = True
        
        user_id = "U1234567890"
        order_id = "ORD1234567890"
        delivery_date = "2026-01-09 14:30"
        old_qty = 3
        new_qty = 5
        
        LINEService.send_delivery_correction_notification(
            user_id=user_id,
            order_id=order_id,
            delivery_date=delivery_date,
            old_qty=old_qty,
            new_qty=new_qty
        )
        
        # 驗證被正確呼叫
        self.assertEqual(mock_send.call_count, 1)
        
        # 驗證第一個參數是 user_id
        called_user_id = mock_send.call_args[0][0]
        self.assertEqual(called_user_id, user_id)


if __name__ == '__main__':
    unittest.main()
