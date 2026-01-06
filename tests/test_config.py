"""
單元測試 - 產品配置
"""
import unittest
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ProductConfig


class TestProductConfig(unittest.TestCase):
    """產品配置測試"""
    
    def test_get_unit_price_11pack_fixed(self):
        """測試 11 盤優惠組固定價格"""
        price = ProductConfig.get_unit_price("土雞蛋11盤", 1)
        self.assertEqual(price, 2500)
    
    def test_get_unit_price_single_pack_1_to_9(self):
        """測試單盤 1-9 盤的價格"""
        for qty in range(1, 10):
            price = ProductConfig.get_unit_price("土雞蛋1盤", qty)
            self.assertEqual(price, 250)
    
    def test_get_unit_price_single_pack_10_to_19(self):
        """測試單盤 10-19 盤的價格"""
        for qty in range(10, 20):
            price = ProductConfig.get_unit_price("土雞蛋1盤", qty)
            self.assertEqual(price, 240)
    
    def test_get_unit_price_single_pack_20_and_above(self):
        """測試單盤 20 盤以上的價格"""
        for qty in [20, 30, 50, 100]:
            price = ProductConfig.get_unit_price("土雞蛋1盤", qty)
            self.assertEqual(price, 230)
    
    def test_get_unit_price_nonexistent_product(self):
        """測試不存在的商品"""
        price = ProductConfig.get_unit_price("不存在的商品", 5)
        self.assertIsNone(price)
    
    def test_bulk_pricing_boundary(self):
        """測試分級定價邊界"""
        # 測試邊界值
        self.assertEqual(ProductConfig.get_unit_price("土雞蛋1盤", 9), 250)
        self.assertEqual(ProductConfig.get_unit_price("土雞蛋1盤", 10), 240)
        self.assertEqual(ProductConfig.get_unit_price("土雞蛋1盤", 19), 240)
        self.assertEqual(ProductConfig.get_unit_price("土雞蛋1盤", 20), 230)


class TestTotalOrderAmount(unittest.TestCase):
    """訂單金額計算測試"""
    
    def test_calculate_order_amount_single_pack(self):
        """測試單盤訂單金額計算"""
        # 5 盤 @ $250 = $1250
        unit_price = ProductConfig.get_unit_price("土雞蛋1盤", 5)
        total = unit_price * 5
        self.assertEqual(total, 1250)
    
    def test_calculate_order_amount_bulk_discount(self):
        """測試有折扣的訂單金額計算"""
        # 15 盤 @ $240 = $3600
        unit_price = ProductConfig.get_unit_price("土雞蛋1盤", 15)
        total = unit_price * 15
        self.assertEqual(total, 3600)
    
    def test_calculate_order_amount_11pack(self):
        """測試 11 盤優惠組訂單金額計算"""
        # 2 組 @ $2500 = $5000
        unit_price = ProductConfig.get_unit_price("土雞蛋11盤", 2)
        total = unit_price * 2
        self.assertEqual(total, 5000)


if __name__ == '__main__':
    unittest.main()
