"""
單元測試 - 表單驗證
"""
import unittest
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation import FormValidator


class TestFormValidator(unittest.TestCase):
    """表單驗證器測試"""
    
    def test_validate_register_form_valid(self):
        """測試有效的註冊表單"""
        data = {
            'name': 'John Doe',
            'phone': '0912345678',
            'address': '台北市信義區',
            'birthDate': '1990-01-15',
            'address2': '公司地址'
        }
        result = FormValidator.validate_register_form(data)
        self.assertIsNone(result)
    
    def test_validate_register_form_empty_name(self):
        """測試空姓名"""
        data = {
            'name': '',
            'phone': '0912345678',
            'address': '台北市信義區'
        }
        result = FormValidator.validate_register_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('姓名' in err for err in result))
    
    def test_validate_register_form_invalid_phone(self):
        """測試無效電話格式"""
        data = {
            'name': 'John Doe',
            'phone': '12345',  # 太短
            'address': '台北市信義區'
        }
        result = FormValidator.validate_register_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('電話' in err for err in result))
    
    def test_validate_register_form_name_too_long(self):
        """測試姓名太長"""
        data = {
            'name': 'a' * 51,  # 超過 50 字
            'phone': '0912345678',
            'address': '台北市信義區'
        }
        result = FormValidator.validate_register_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('長度' in err for err in result))
    
    def test_validate_register_form_invalid_date(self):
        """測試無效日期"""
        data = {
            'name': 'John Doe',
            'phone': '0912345678',
            'address': '台北市信義區',
            'birthDate': '1990/01/15'  # 格式錯誤
        }
        result = FormValidator.validate_register_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('日期' in err for err in result))
    
    def test_validate_order_form_valid(self):
        """測試有效的訂單表單"""
        data = {
            'productId': 'prod_test123',
            'itemName': '土雞蛋',
            'qty': '5',
            'remarks': '下午配送',
            'paymentMethod': 'transfer'
        }
        result = FormValidator.validate_order_form(data)
        self.assertIsNone(result)
    
    def test_validate_order_form_invalid_qty(self):
        """測試無效數量"""
        data = {
            'productId': 'prod_test123',
            'itemName': '土雞蛋',
            'qty': '0',  # 小於 1
            'paymentMethod': 'transfer'
        }
        result = FormValidator.validate_order_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('數量' in err for err in result))
    
    def test_validate_order_form_qty_too_large(self):
        """測試數量過大"""
        data = {
            'productId': 'prod_test123',
            'itemName': '土雞蛋',
            'qty': '1001',
            'paymentMethod': 'transfer'
        }
        result = FormValidator.validate_order_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('數量' in err for err in result))
    
    def test_validate_order_form_invalid_payment_method(self):
        """測試無效付款方式"""
        data = {
            'productId': 'prod_test123',
            'itemName': '土雞蛋',
            'qty': '5',
            'paymentMethod': 'invalid'
        }
        result = FormValidator.validate_order_form(data)
        self.assertIsNotNone(result)
        self.assertTrue(any('付款方式' in err for err in result))
    
    def test_is_valid_phone_correct_format(self):
        """測試正確的電話格式"""
        self.assertTrue(FormValidator._is_valid_phone('0912345678'))
        self.assertTrue(FormValidator._is_valid_phone('0912345678'))
    
    def test_is_valid_phone_invalid_format(self):
        """測試無效的電話格式"""
        self.assertFalse(FormValidator._is_valid_phone('123'))
        self.assertFalse(FormValidator._is_valid_phone('abc'))
        self.assertFalse(FormValidator._is_valid_phone(''))
    
    def test_is_valid_date_correct_format(self):
        """測試正確的日期格式"""
        self.assertTrue(FormValidator._is_valid_date('1990-01-15'))
        self.assertTrue(FormValidator._is_valid_date('2023-12-25'))
    
    def test_is_valid_date_invalid_format(self):
        """測試無效的日期格式"""
        self.assertFalse(FormValidator._is_valid_date('1990/01/15'))
        self.assertFalse(FormValidator._is_valid_date('15-01-1990'))
        self.assertFalse(FormValidator._is_valid_date(''))
        self.assertFalse(FormValidator._is_valid_date('1990-13-01'))  # 無效月份
        self.assertFalse(FormValidator._is_valid_date('1990-02-30'))  # 無效日期


class TestPasswordValidator(unittest.TestCase):
    """密碼驗證測試"""
    
    def test_validate_login_password_valid(self):
        """測試有效密碼"""
        result = FormValidator.validate_login_password('password123')
        self.assertIsNone(result)
    
    def test_validate_login_password_empty(self):
        """測試空密碼"""
        result = FormValidator.validate_login_password('')
        self.assertIsNotNone(result)
    
    def test_validate_login_password_too_short(self):
        """測試太短的密碼"""
        result = FormValidator.validate_login_password('ab')
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
