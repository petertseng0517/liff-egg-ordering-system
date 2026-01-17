"""
應用程式配置管理
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Config:
    """基礎配置"""
    # Flask 配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # 管理員配置 - 從環境變數讀取帳號密碼
    # 格式: ADMIN_ACCOUNTS=admin:admin123,manager:manager123
    # 在 .env 檔案中設置，不要提交到 Git
    @property
    def ADMIN_ACCOUNTS(self):
        """從環境變數解析帳號密碼對"""
        accounts_str = os.getenv('ADMIN_ACCOUNTS', 'admin:admin123,manager:manager123')
        accounts = {}
        for pair in accounts_str.split(','):
            if ':' in pair:
                username, password = pair.split(':', 1)
                accounts[username.strip()] = password.strip()
        return accounts
    MAX_LOGIN_ATTEMPTS = 5  # 最多嘗試次數
    LOGIN_ATTEMPT_TIMEOUT = 300  # 秒 (5分鐘)
    SESSION_TIMEOUT = 180  # 秒 (3分鐘) - 管理後台超時時間
    
    # 時區設置 - 台灣時區
    TIMEZONE = 'Asia/Taipei'
    
    # Google Sheets 配置
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    GOOGLE_SHEETS_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Firebase Firestore 配置
    USE_FIRESTORE = os.getenv('USE_FIRESTORE', 'false').lower() == 'true'
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL')
    FIREBASE_CLIENT_ID = os.getenv('FIREBASE_CLIENT_ID')
    
    # LINE Bot 配置
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    # ECPay 配置 (測試環境)
    ECPAY_MERCHANT_ID = os.getenv('ECPAY_MERCHANT_ID', '2000132')
    ECPAY_HASH_KEY = os.getenv('ECPAY_HASH_KEY', '5294y06JbISpM5x9')
    ECPAY_HASH_IV = os.getenv('ECPAY_HASH_IV', 'v77hoKGq4kWxNNIS')
    ECPAY_ACTION_URL = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'
    
    # 應用程式基礎 URL
    APP_BASE_URL = os.getenv('APP_BASE_URL', None)
    
    # 日誌配置
    LOG_FILE = 'ecpay_callback.log'
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


class ProductConfig:
    """產品配置"""
    PRODUCTS = {
        "土雞蛋11盤": 2500,
        "土雞蛋1盤": 250
    }
    
    # 土雞蛋 1 盤的分級定價
    BULK_PRICING = {
        "土雞蛋1盤": [
            (1, 9, 250),      # 1-9盤: $250
            (10, 19, 240),    # 10-19盤: $240
            (20, float('inf'), 230)  # 20盤以上: $230
        ]
    }
    
    @staticmethod
    def get_unit_price(item_name, qty):
        """獲取單位價格，考慮批量折扣"""
        if item_name not in ProductConfig.BULK_PRICING:
            return ProductConfig.PRODUCTS.get(item_name)
        
        for min_qty, max_qty, price in ProductConfig.BULK_PRICING[item_name]:
            if min_qty <= qty <= max_qty:
                return price
        return ProductConfig.PRODUCTS.get(item_name, 0)
