"""
表單驗證模組
"""
import re


class FormValidator:
    """表單驗證工具"""
    
    @staticmethod
    def validate_register_form(data):
        """驗證註冊表單"""
        errors = []
        
        # 驗證姓名
        name = data.get('name', '').strip()
        if not name:
            errors.append("姓名不能為空")
        elif len(name) > 50:
            errors.append("姓名長度不能超過 50 個字元")
        
        # 驗證電話
        phone = data.get('phone', '').strip()
        if not phone:
            errors.append("聯絡電話不能為空")
        elif not FormValidator._is_valid_phone(phone):
            errors.append("電話格式不正確（請輸入 10 位數字）")
        
        # 驗證地址
        address = data.get('address', '').strip()
        if not address:
            errors.append("配送地址不能為空")
        elif len(address) > 200:
            errors.append("地址長度不能超過 200 個字元")
        
        # 驗證出生日期 (選填)
        birthdate = data.get('birthDate', '').strip()
        if birthdate and not FormValidator._is_valid_date(birthdate):
            errors.append("出生日期格式不正確")
        
        # 驗證第二地址 (選填)
        address2 = data.get('address2', '').strip()
        if address2 and len(address2) > 200:
            errors.append("第二地址長度不能超過 200 個字元")
        
        return errors if errors else None
    
    @staticmethod
    def validate_order_form(data):
        """驗證訂單表單"""
        errors = []
        
        # 驗證商品 ID
        product_id = data.get('productId', '').strip()
        if not product_id:
            errors.append("商品 ID 不能為空")
        
        # 驗證商品名稱
        item_name = data.get('itemName', '').strip()
        if not item_name:
            errors.append("商品名稱不能為空")
        
        # 驗證數量
        try:
            qty = int(data.get('qty', 1))
            if qty < 1:
                errors.append("數量必須大於 0")
            elif qty > 1000:
                errors.append("單次訂購數量不能超過 1000")
        except (ValueError, TypeError):
            errors.append("數量格式不正確")
        
        # 驗證付款方式
        payment_method = data.get('paymentMethod', '').strip()
        if payment_method not in ['transfer', 'ecpay']:
            errors.append("付款方式不正確")
        
        # 驗證備註 (選填)
        remarks = data.get('remarks', '').strip()
        if remarks and len(remarks) > 500:
            errors.append("備註長度不能超過 500 個字元")
        
        return errors if errors else None
    
    @staticmethod
    def validate_login_password(password):
        """驗證登入密碼"""
        if not password:
            return "密碼不能為空"
        if len(password) < 3:
            return "密碼長度過短"
        return None
    
    @staticmethod
    def _is_valid_phone(phone):
        """驗證電話號碼格式"""
        # 台灣電話：09xx-xxxxxx 或 10 位數字
        phone_pattern = r'^\d{10}$|^09\d{8}$'
        return bool(re.match(phone_pattern, phone.replace('-', '')))
    
    @staticmethod
    def _is_valid_date(date_str):
        """驗證日期格式 (YYYY-MM-DD)"""
        try:
            from datetime import datetime
            # 使用 datetime 來驗證日期的有效性
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except (ValueError, AttributeError, TypeError):
            return False
