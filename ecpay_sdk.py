import hashlib
import urllib.parse
from datetime import datetime
import pytz

class ECPaySDK:
    def __init__(self, merchant_id, hash_key, hash_iv, action_url):
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.action_url = action_url

    def generate_check_mac_value(self, params):
        # 1. Sort parameters
        filtered_params = {k: v for k, v in params.items() if k != 'CheckMacValue'}
        sorted_params = sorted(filtered_params.items())

        # 2. Concatenate with ampersand
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])

        # 3. Sandwich with HashKey and HashIV
        raw_string = f"HashKey={self.hash_key}&{query_string}&HashIV={self.hash_iv}"

        # 4. URL Encode with custom replacements
        # quote_plus encodes spaces as '+' which ECPay expects.
        encoded_string = urllib.parse.quote_plus(raw_string).lower()

        # ECPay's specific replacements for .NET encoding (must be lower case hex)
        encoded_string = encoded_string.replace('%2d', '-')
        encoded_string = encoded_string.replace('%5f', '_')
        encoded_string = encoded_string.replace('%2e', '.')
        encoded_string = encoded_string.replace('%21', '!')
        encoded_string = encoded_string.replace('%2a', '*')
        encoded_string = encoded_string.replace('%28', '(')
        encoded_string = encoded_string.replace('%29', ')')

        # 5. SHA256 Hash
        hashed_string = hashlib.sha256(encoded_string.encode('utf-8')).hexdigest()

        # 6. Convert to Uppercase
        return hashed_string.upper()

    def create_order(self, order_id, total_amount, item_name, return_url, client_back_url, order_result_url):
        params = {
            "MerchantID": self.merchant_id,
            "MerchantTradeNo": order_id,  # Must be unique per transaction
            "MerchantTradeDate": datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y/%m/%d %H:%M:%S"),
            "PaymentType": "aio",
            "TotalAmount": str(total_amount),
            "TradeDesc": "EggOrder",
            "ItemName": item_name,
            "ReturnURL": return_url, # Server-side callback (POST)
            "ChoosePayment": "ALL",
            "ClientBackURL": client_back_url, # Client-side redirect (GET)
            "EncryptType": "1",
            "ItemURL": "",
            "Remark": "",
            "OrderResultURL": order_result_url, # Can be used to redirect client after payment to a specific result page
            "NeedExtraPaidInfo": "N",
        }
        
        # Calculate CheckMacValue
        check_mac_value = self.generate_check_mac_value(params)
        params["CheckMacValue"] = check_mac_value
        
        return params
