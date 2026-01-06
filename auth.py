"""
認證與密碼管理模組
"""
import hashlib
import hmac
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, jsonify
from config import Config


class PasswordManager:
    """密碼管理 (使用 bcrypt 更安全)"""
    
    @staticmethod
    def hash_password(password):
        """密碼加密 (簡化版，建議生產環境使用 bcrypt)"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            b'salt',
            100000
        ).hex()
    
    @staticmethod
    def verify_password(password, hashed):
        """驗證密碼"""
        return PasswordManager.hash_password(password) == hashed


class LoginAttemptTracker:
    """登入嘗試追蹤 - 防止暴力破解"""
    
    def __init__(self):
        self.attempts = {}  # {ip: {'count': int, 'timestamp': datetime}}
    
    def get_key(self, identifier):
        """生成追蹤鑰匙"""
        return f"login_attempt_{identifier}"
    
    def record_attempt(self, identifier):
        """記錄登入嘗試"""
        key = self.get_key(identifier)
        if key not in self.attempts:
            self.attempts[key] = {'count': 0, 'timestamp': datetime.now()}
        
        self.attempts[key]['count'] += 1
        self.attempts[key]['timestamp'] = datetime.now()
    
    def is_locked(self, identifier):
        """檢查是否被鎖定"""
        key = self.get_key(identifier)
        if key not in self.attempts:
            return False
        
        attempt_info = self.attempts[key]
        # 檢查是否超過時間限制
        if datetime.now() - attempt_info['timestamp'] > timedelta(seconds=Config.LOGIN_ATTEMPT_TIMEOUT):
            del self.attempts[key]
            return False
        
        return attempt_info['count'] >= Config.MAX_LOGIN_ATTEMPTS
    
    def get_remaining_time(self, identifier):
        """取得剩餘鎖定時間 (秒)"""
        key = self.get_key(identifier)
        if key not in self.attempts:
            return 0
        
        elapsed = (datetime.now() - self.attempts[key]['timestamp']).total_seconds()
        remaining = Config.LOGIN_ATTEMPT_TIMEOUT - elapsed
        return max(0, int(remaining))
    
    def reset(self, identifier):
        """重置嘗試計數"""
        key = self.get_key(identifier)
        if key in self.attempts:
            del self.attempts[key]


# 全局追蹤器實例
login_tracker = LoginAttemptTracker()


def require_admin_login(f):
    """管理員登入驗證裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def require_admin_login_api(f):
    """API 管理員登入驗證裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({"error": "Unauthorized", "msg": "請先登入"}), 401
        return f(*args, **kwargs)
    return decorated_function
