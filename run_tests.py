#!/usr/bin/env python3
"""
運行所有單元測試的腳本
"""
import sys
import os
import unittest

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # 發現並運行 tests 目錄中的所有測試
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回適當的退出代碼
    sys.exit(0 if result.wasSuccessful() else 1)
