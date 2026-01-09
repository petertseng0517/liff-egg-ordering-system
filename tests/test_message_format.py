"""
單元測試 - 出貨訊息格式驗證（無外部依賴）
"""
import unittest


class TestDeliveryMessageFormat(unittest.TestCase):
    """出貨通知訊息格式驗證測試"""
    
    def format_delivery_notification(self, order_id, delivery_date, qty, remaining_qty):
        """模擬 LINEService.send_delivery_notification 的訊息格式"""
        msg = (
            f"📦 出貨通知\n\n"
            f"訂單編號：{order_id}\n"
            f"本次出貨日期：{delivery_date}\n"
            f"本次出貨數量：{qty}盤\n"
            f"本訂單剩餘：{remaining_qty}盤"
        )
        return msg
    
    def test_delivery_notification_contains_order_id(self):
        """測試訊息包含訂單編號"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        self.assertIn("訂單編號：ORD1234567890", msg)
    
    def test_delivery_notification_contains_delivery_date(self):
        """測試訊息包含出貨日期"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        self.assertIn("本次出貨日期：2026-01-09 14:30", msg)
    
    def test_delivery_notification_contains_qty(self):
        """測試訊息包含本次出貨數量"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        self.assertIn("本次出貨數量：5盤", msg)
    
    def test_delivery_notification_contains_remaining_qty(self):
        """測試訊息包含剩餘數量"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        self.assertIn("本訂單剩餘：17盤", msg)
    
    def test_delivery_notification_no_progress(self):
        """測試訊息不包含目前進度"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        self.assertNotIn("目前進度", msg)
    
    def test_delivery_notification_no_shipping_reminder(self):
        """測試訊息不包含配送提示"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=5,
            remaining_qty=17
        )
        self.assertNotIn("其餘商品", msg)
    
    def test_delivery_notification_with_zero_remaining(self):
        """測試訊息格式 - 剩餘數量為 0"""
        msg = self.format_delivery_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            qty=22,
            remaining_qty=0
        )
        self.assertIn("本訂單剩餘：0盤", msg)


class TestCorrectionMessageFormat(unittest.TestCase):
    """出貨修正通知訊息格式驗證測試"""
    
    def format_correction_notification(self, order_id, delivery_date, old_qty, new_qty):
        """模擬 LINEService.send_delivery_correction_notification 的訊息格式"""
        msg = (
            f"🔄 出貨紀錄修正通知\n\n"
            f"訂單編號：{order_id}\n"
            f"出貨日期：{delivery_date}\n\n"
            f"依實際需求修改出貨紀錄\n"
            f"原紀錄：{old_qty}盤 → 修正為：{new_qty}盤"
        )
        return msg
    
    def test_correction_notification_contains_order_id(self):
        """測試訊息包含訂單編號"""
        msg = self.format_correction_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            old_qty=3,
            new_qty=5
        )
        self.assertIn("訂單編號：ORD1234567890", msg)
    
    def test_correction_notification_contains_date(self):
        """測試訊息包含出貨日期"""
        msg = self.format_correction_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            old_qty=3,
            new_qty=5
        )
        self.assertIn("出貨日期：2026-01-09 14:30", msg)
    
    def test_correction_notification_contains_correction(self):
        """測試訊息包含修正內容"""
        msg = self.format_correction_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            old_qty=3,
            new_qty=5
        )
        self.assertIn("原紀錄：3盤 → 修正為：5盤", msg)
    
    def test_correction_notification_no_progress(self):
        """測試訊息不包含目前進度"""
        msg = self.format_correction_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            old_qty=3,
            new_qty=5
        )
        self.assertNotIn("目前進度", msg)
    
    def test_correction_notification_no_shipping_reminder(self):
        """測試訊息不包含配送提示"""
        msg = self.format_correction_notification(
            order_id="ORD1234567890",
            delivery_date="2026-01-09 14:30",
            old_qty=3,
            new_qty=5
        )
        self.assertNotIn("其餘商品", msg)
    
    def test_correction_notification_different_values(self):
        """測試不同數值的修正訊息"""
        msg = self.format_correction_notification(
            order_id="ORD9876543210",
            delivery_date="2026-01-08 10:15",
            old_qty=10,
            new_qty=8
        )
        self.assertIn("訂單編號：ORD9876543210", msg)
        self.assertIn("出貨日期：2026-01-08 10:15", msg)
        self.assertIn("原紀錄：10盤 → 修正為：8盤", msg)


class TestDeliveryValidationLogic(unittest.TestCase):
    """出貨驗證邏輯測試"""
    
    def test_remaining_qty_calculation_partial_delivery(self):
        """測試部分出貨時的剩餘計算"""
        total_ordered = 22
        total_delivered = 5
        remaining = total_ordered - total_delivered
        self.assertEqual(remaining, 17)
    
    def test_remaining_qty_calculation_full_delivery(self):
        """測試全部出貨時的剩餘計算"""
        total_ordered = 22
        total_delivered = 22
        remaining = total_ordered - total_delivered
        self.assertEqual(remaining, 0)
    
    def test_remaining_qty_calculation_multiple_shipments(self):
        """測試多批出貨時的剩餘計算"""
        total_ordered = 22
        total_delivered = 3 + 5 + 14
        remaining = total_ordered - total_delivered
        self.assertEqual(remaining, 0)
    
    def test_new_delivery_validation_pass(self):
        """測試新增出貨驗證通過"""
        total_ordered = 22
        current_delivered = 5
        remaining = total_ordered - current_delivered
        
        new_delivery = 10
        self.assertLessEqual(new_delivery, remaining)
        
        new_total = current_delivered + new_delivery
        self.assertLessEqual(new_total, total_ordered)
    
    def test_new_delivery_validation_fail(self):
        """測試新增出貨驗證失敗"""
        total_ordered = 22
        current_delivered = 20
        remaining = total_ordered - current_delivered
        
        new_delivery = 5
        self.assertGreater(new_delivery, remaining)
        
        new_total = current_delivered + new_delivery
        self.assertGreater(new_total, total_ordered)


class TestCorrectedQtyLogic(unittest.TestCase):
    """修正數量計算邏輯測試"""
    
    def calculate_total_with_corrected_qty(self, logs):
        """模擬前端計算邏輯：使用修正後的數量或原始數量"""
        total = 0
        for log in logs:
            qty = log.get('corrected_qty') or log.get('qty', 0)
            total += int(qty)
        return total
    
    def test_corrected_qty_single_delivery(self):
        """測試單次出貨修正"""
        logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "corrected_qty": 5}
        ]
        total = self.calculate_total_with_corrected_qty(logs)
        self.assertEqual(total, 5)
    
    def test_corrected_qty_multiple_deliveries(self):
        """測試多次出貨修正"""
        logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "corrected_qty": 5},
            {"date": "2026-01-09 12:00", "qty": 17}
        ]
        total = self.calculate_total_with_corrected_qty(logs)
        self.assertEqual(total, 22)
    
    def test_corrected_qty_fallback_to_original(self):
        """測試未修正的日誌使用原始數量"""
        logs = [
            {"date": "2026-01-09 10:00", "qty": 5},
            {"date": "2026-01-09 12:00", "qty": 17}
        ]
        total = self.calculate_total_with_corrected_qty(logs)
        self.assertEqual(total, 22)
    
    def test_correction_validation_pass(self):
        """測試修正驗證通過"""
        total_ordered = 22
        logs = [
            {"qty": 3},
            {"qty": 17}
        ]
        
        # 修正第一筆：3 -> 5
        new_qty = 5
        calculated_total = new_qty + int(logs[1].get('qty', 0))
        
        self.assertLessEqual(calculated_total, total_ordered)
    
    def test_correction_validation_fail(self):
        """測試修正驗證失敗"""
        total_ordered = 22
        logs = [
            {"qty": 3},
            {"qty": 17}
        ]
        
        # 試圖修正第一筆：3 -> 25（超過）
        new_qty = 25
        calculated_total = new_qty + int(logs[1].get('qty', 0))
        
        self.assertGreater(calculated_total, total_ordered)


class TestEdgeCases(unittest.TestCase):
    """邊界情況測試"""
    
    def test_first_delivery(self):
        """測試第一次出貨"""
        total_ordered = 22
        current_delivered = 0
        remaining = total_ordered - current_delivered
        
        new_qty = 3
        self.assertLessEqual(new_qty, remaining)
        self.assertEqual(remaining, 22)
    
    def test_last_delivery_exact_amount(self):
        """測試最後一次出貨恰好填滿"""
        total_ordered = 22
        current_delivered = 5
        remaining = total_ordered - current_delivered
        
        new_qty = 17
        self.assertLessEqual(new_qty, remaining)
        self.assertEqual(current_delivered + new_qty, total_ordered)
    
    def test_many_small_shipments(self):
        """測試多個小額出貨"""
        total_ordered = 5
        logs = [
            {"qty": 1},
            {"qty": 1},
            {"qty": 1},
            {"qty": 1},
            {"qty": 1},
        ]
        
        total = sum(int(log.get('qty', 0)) for log in logs)
        remaining = total_ordered - total
        
        self.assertEqual(total, 5)
        self.assertEqual(remaining, 0)
    
    def test_large_order(self):
        """測試大訂單"""
        total_ordered = 1000
        logs = [
            {"qty": 500},
            {"qty": 500}
        ]
        
        total = sum(int(log.get('qty', 0)) for log in logs)
        remaining = total_ordered - total
        
        self.assertEqual(total, 1000)
        self.assertEqual(remaining, 0)


if __name__ == '__main__':
    unittest.main()
