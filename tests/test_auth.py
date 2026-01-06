"""
單元測試 - 認證與密碼管理
"""
import unittest
import sys
import os
from datetime import datetime, timedelta

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import PasswordManager, LoginAttemptTracker


class TestPasswordManager(unittest.TestCase):
    """密碼管理器測試"""
    
    def test_hash_password(self):
        """測試密碼加密"""
        password = "test_password"
        hashed = PasswordManager.hash_password(password)
        self.assertIsNotNone(hashed)
        self.assertNotEqual(hashed, password)
        self.assertIsInstance(hashed, str)
    
    def test_verify_password_correct(self):
        """測試正確密碼驗證"""
        password = "test_password"
        hashed = PasswordManager.hash_password(password)
        self.assertTrue(PasswordManager.verify_password(password, hashed))
    
    def test_verify_password_incorrect(self):
        """測試錯誤密碼驗證"""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = PasswordManager.hash_password(password)
        self.assertFalse(PasswordManager.verify_password(wrong_password, hashed))
    
    def test_hash_consistency(self):
        """測試相同密碼產生相同 hash"""
        password = "test_password"
        hash1 = PasswordManager.hash_password(password)
        hash2 = PasswordManager.hash_password(password)
        self.assertEqual(hash1, hash2)


class TestLoginAttemptTracker(unittest.TestCase):
    """登入嘗試追蹤器測試"""
    
    def setUp(self):
        """測試前初始化"""
        self.tracker = LoginAttemptTracker()
        self.test_ip = "192.168.1.1"
    
    def test_get_key(self):
        """測試鑰匙生成"""
        key = self.tracker.get_key(self.test_ip)
        self.assertEqual(key, f"login_attempt_{self.test_ip}")
    
    def test_record_first_attempt(self):
        """測試記錄第一次嘗試"""
        self.tracker.record_attempt(self.test_ip)
        key = self.tracker.get_key(self.test_ip)
        self.assertIn(key, self.tracker.attempts)
        self.assertEqual(self.tracker.attempts[key]['count'], 1)
    
    def test_record_multiple_attempts(self):
        """測試記錄多次嘗試"""
        for i in range(3):
            self.tracker.record_attempt(self.test_ip)
        key = self.tracker.get_key(self.test_ip)
        self.assertEqual(self.tracker.attempts[key]['count'], 3)
    
    def test_is_locked_not_exceeded(self):
        """測試未達鎖定限制"""
        for i in range(3):
            self.tracker.record_attempt(self.test_ip)
        self.assertFalse(self.tracker.is_locked(self.test_ip))
    
    def test_is_locked_exceeded(self):
        """測試超過鎖定限制"""
        from config import Config
        for i in range(Config.MAX_LOGIN_ATTEMPTS):
            self.tracker.record_attempt(self.test_ip)
        self.assertTrue(self.tracker.is_locked(self.test_ip))
    
    def test_is_locked_timeout_expired(self):
        """測試鎖定超時過期"""
        from config import Config
        # 記錄多次嘗試
        for i in range(Config.MAX_LOGIN_ATTEMPTS):
            self.tracker.record_attempt(self.test_ip)
        
        # 模擬時間過期
        key = self.tracker.get_key(self.test_ip)
        self.tracker.attempts[key]['timestamp'] = datetime.now() - timedelta(
            seconds=Config.LOGIN_ATTEMPT_TIMEOUT + 1
        )
        
        # 應該不再被鎖定
        self.assertFalse(self.tracker.is_locked(self.test_ip))
    
    def test_get_remaining_time(self):
        """測試取得剩餘時間"""
        from config import Config
        self.tracker.record_attempt(self.test_ip)
        remaining = self.tracker.get_remaining_time(self.test_ip)
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, Config.LOGIN_ATTEMPT_TIMEOUT)
    
    def test_reset_attempts(self):
        """測試重置嘗試"""
        self.tracker.record_attempt(self.test_ip)
        key = self.tracker.get_key(self.test_ip)
        self.assertIn(key, self.tracker.attempts)
        
        self.tracker.reset(self.test_ip)
        self.assertNotIn(key, self.tracker.attempts)


if __name__ == '__main__':
    unittest.main()
