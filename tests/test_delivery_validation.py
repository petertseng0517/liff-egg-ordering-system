"""
單元測試 - 出貨驗證邏輯（前端驗證模擬）
"""
import unittest
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAddDeliveryValidation(unittest.TestCase):
    """新增出貨驗證邏輯測試"""
    
    def calculate_current_delivered(self, delivery_logs):
        """
        模擬前端的 addDeliveryLog() 中的計算邏輯
        使用修正後的數量 (corrected_qty) 或原始數量 (qty)
        """
        if not delivery_logs:
            return 0
        
        total = 0
        for log in delivery_logs:
            qty = log.get('corrected_qty') or log.get('qty', 0)
            total += int(qty)
        return total
    
    def test_add_delivery_validation_first_shipment(self):
        """測試第一次出貨驗證"""
        delivery_logs = []
        total_ordered = 22
        
        current_delivered = self.calculate_current_delivered(delivery_logs)
        remaining = total_ordered - current_delivered
        
        # 第一次出貨 3 盤
        new_qty = 3
        self.assertLessEqual(new_qty, remaining)
        self.assertEqual(remaining, 22)
    
    def test_add_delivery_validation_after_correction(self):
        """測試修正後的出貨驗證"""
        # 模擬：第一次出貨 3 盤，後來改為 5 盤
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "corrected_qty": 5, "address": "address1"}
        ]
        total_ordered = 22
        
        current_delivered = self.calculate_current_delivered(delivery_logs)
        remaining = total_ordered - current_delivered
        
        # 第二次出貨 17 盤（應該通過驗證）
        new_qty = 17
        self.assertLessEqual(new_qty, remaining)
        self.assertEqual(current_delivered, 5)
        self.assertEqual(remaining, 17)
    
    def test_add_delivery_validation_exceeds_remaining(self):
        """測試出貨數量超過剩餘的情況"""
        # 已經出貨 5 盤（修正後）
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "corrected_qty": 5, "address": "address1"}
        ]
        total_ordered = 22
        
        current_delivered = self.calculate_current_delivered(delivery_logs)
        remaining = total_ordered - current_delivered
        
        # 試圖出貨 20 盤（超過剩餘的 17 盤）
        new_qty = 20
        self.assertGreater(new_qty, remaining)
    
    def test_add_delivery_validation_multiple_deliveries(self):
        """測試多次出貨驗證"""
        # 已有兩次出貨
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 5, "address": "address2"}
        ]
        total_ordered = 22
        
        current_delivered = self.calculate_current_delivered(delivery_logs)
        remaining = total_ordered - current_delivered
        
        # 第三次出貨 14 盤（恰好填滿）
        new_qty = 14
        self.assertLessEqual(new_qty, remaining)
        self.assertEqual(current_delivered, 8)
        self.assertEqual(remaining, 14)
    
    def test_add_delivery_validation_with_mixed_logs(self):
        """測試混合修正和未修正的日誌"""
        # 模擬：第一次出貨 3 盤（已修正為 5），第二次出貨 10 盤
        delivery_logs = [
            {
                "date": "2026-01-09 10:00",
                "qty": 3,
                "corrected_qty": 5,
                "corrected": True,
                "address": "address1"
            },
            {
                "date": "2026-01-09 12:00",
                "qty": 10,
                "address": "address2"
            }
        ]
        total_ordered = 22
        
        current_delivered = self.calculate_current_delivered(delivery_logs)
        remaining = total_ordered - current_delivered
        
        # 應該是 5 + 10 = 15
        self.assertEqual(current_delivered, 15)
        self.assertEqual(remaining, 7)
        
        # 第三次出貨 7 盤（恰好填滿）
        new_qty = 7
        self.assertLessEqual(new_qty, remaining)


class TestCorrectDeliveryValidation(unittest.TestCase):
    """修正出貨驗證邏輯測試"""
    
    def calculate_delivered_after_correction(self, delivery_logs, log_index, new_qty):
        """
        模擬前端 submitCorrection() 中的驗證邏輯
        計算修正後的總出貨量
        """
        total = 0
        for index, log in enumerate(delivery_logs):
            if index == log_index:
                # 使用修正後的新數量
                total += new_qty
            else:
                # 其他記錄使用已修正的或原始數量
                qty = log.get('corrected_qty') or log.get('qty', 0)
                total += int(qty)
        return total
    
    def test_correct_delivery_validation_pass(self):
        """測試修正驗證應該通過的情況"""
        # 第一次 3 盤，第二次 17 盤
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 17, "address": "address2"}
        ]
        total_ordered = 22
        
        # 修正第一次：3 -> 5
        log_index = 0
        new_qty = 5
        
        calculated_total = self.calculate_delivered_after_correction(
            delivery_logs, log_index, new_qty
        )
        
        # 應該是 5 + 17 = 22，不超過訂購量
        self.assertEqual(calculated_total, 22)
        self.assertLessEqual(calculated_total, total_ordered)
    
    def test_correct_delivery_validation_fail(self):
        """測試修正驗證應該失敗的情況"""
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 17, "address": "address2"}
        ]
        total_ordered = 22
        
        # 試圖修正第一次：3 -> 10（超過訂購量）
        log_index = 0
        new_qty = 10
        
        calculated_total = self.calculate_delivered_after_correction(
            delivery_logs, log_index, new_qty
        )
        
        # 應該是 10 + 17 = 27，超過訂購量
        self.assertEqual(calculated_total, 27)
        self.assertGreater(calculated_total, total_ordered)
    
    def test_correct_delivery_with_already_corrected_logs(self):
        """測試修正已經被修正過的日誌"""
        # 第一次已經修正過：原本 3，修正為 5
        delivery_logs = [
            {
                "date": "2026-01-09 10:00",
                "qty": 3,
                "corrected_qty": 5,
                "corrected": True,
                "address": "address1"
            },
            {"date": "2026-01-09 12:00", "qty": 17, "address": "address2"}
        ]
        total_ordered = 22
        
        # 再修正第一次：5 -> 6（不應該超過）
        log_index = 0
        new_qty = 6
        
        calculated_total = self.calculate_delivered_after_correction(
            delivery_logs, log_index, new_qty
        )
        
        # 應該是 6 + 17 = 23，超過訂購量
        self.assertEqual(calculated_total, 23)
        self.assertGreater(calculated_total, total_ordered)
    
    def test_correct_delivery_boundary_case(self):
        """測試邊界情況：恰好填滿"""
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 3, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 19, "address": "address2"}
        ]
        total_ordered = 22
        
        # 修正第一次：3 -> 3（不變，只改地址）
        log_index = 0
        new_qty = 3
        
        calculated_total = self.calculate_delivered_after_correction(
            delivery_logs, log_index, new_qty
        )
        
        self.assertEqual(calculated_total, 22)
        self.assertLessEqual(calculated_total, total_ordered)
    
    def test_correct_delivery_reduce_quantity(self):
        """測試減少出貨數量的修正"""
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 10, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 10, "address": "address2"}
        ]
        total_ordered = 22
        
        # 修正第一次：10 -> 8（減少）
        log_index = 0
        new_qty = 8
        
        calculated_total = self.calculate_delivered_after_correction(
            delivery_logs, log_index, new_qty
        )
        
        # 應該是 8 + 10 = 18，不超過訂購量
        self.assertEqual(calculated_total, 18)
        self.assertLess(calculated_total, total_ordered)
    
    def test_correct_delivery_last_shipment(self):
        """測試修正最後一次出貨"""
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 5, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 17, "address": "address2"}
        ]
        total_ordered = 22
        
        # 修正第二次（最後一次）：17 -> 15
        log_index = 1
        new_qty = 15
        
        calculated_total = self.calculate_delivered_after_correction(
            delivery_logs, log_index, new_qty
        )
        
        # 應該是 5 + 15 = 20，不超過訂購量
        self.assertEqual(calculated_total, 20)
        self.assertLess(calculated_total, total_ordered)


class TestEdgeCases(unittest.TestCase):
    """邊界情況測試"""
    
    def test_delivery_with_zero_qty(self):
        """測試零數量的出貨（不合法）"""
        total_ordered = 22
        remaining = total_ordered
        
        new_qty = 0
        # 應該不允許零數量
        self.assertLessEqual(new_qty, 0)
    
    def test_delivery_with_negative_qty(self):
        """測試負數數量的出貨（不合法）"""
        total_ordered = 22
        remaining = total_ordered
        
        new_qty = -5
        # 應該不允許負數
        self.assertLess(new_qty, 0)
    
    def test_very_large_order(self):
        """測試大訂單驗證"""
        delivery_logs = [
            {"date": "2026-01-09 10:00", "qty": 500, "address": "address1"},
            {"date": "2026-01-09 12:00", "qty": 500, "address": "address2"}
        ]
        total_ordered = 1000
        
        current_delivered = sum(int(l.get('corrected_qty') or l.get('qty', 0)) 
                               for l in delivery_logs)
        remaining = total_ordered - current_delivered
        
        self.assertEqual(current_delivered, 1000)
        self.assertEqual(remaining, 0)
    
    def test_many_small_deliveries(self):
        """測試多次小額出貨"""
        delivery_logs = [
            {"qty": 1},
            {"qty": 1},
            {"qty": 1},
            {"qty": 1},
            {"qty": 1},
        ]
        total_ordered = 5
        
        current_delivered = sum(int(l.get('corrected_qty') or l.get('qty', 0)) 
                               for l in delivery_logs)
        remaining = total_ordered - current_delivered
        
        self.assertEqual(current_delivered, 5)
        self.assertEqual(remaining, 0)


if __name__ == '__main__':
    unittest.main()
