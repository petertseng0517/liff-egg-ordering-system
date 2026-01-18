# 單元測試文件指南

## 測試文件結構

```
tests/
├── __init__.py
├── test_app.py              - Flask 應用基本測試
├── test_auth.py             - 認證與密碼管理測試
├── test_config.py           - 產品配置測試
├── test_delivery.py         - 配送測試
├── test_delivery_validation.py - 配送驗證測試
├── test_message_format.py   - 訊息格式測試
├── test_validation.py       - 表單驗證測試
├── test_line_service.py     - LINE 訊息服務測試 (新)
├── test_firestore_service.py - Firebase Firestore 服務測試 (新)
├── test_member_routes.py    - 會員路由整合測試 (新)
└── test_admin_routes.py     - 管理員路由整合測試 (新)
```

## 現有測試覆蓋範圍

### 已有測試
| 模組 | 測試文件 | 覆蓋內容 |
|------|---------|---------|
| 認證 | `test_auth.py` | 密碼加密、登入追蹤 |
| 配置 | `test_config.py` | 產品定價、分級優惠 |
| 驗證 | `test_validation.py` | 表單驗證、電話格式、日期格式 |
| 應用 | `test_app.py` | 路由基本測試、404 錯誤 |
| 配送 | `test_delivery*.py` | 配送邏輯、配送驗證 |

### 新增測試
| 模組 | 測試文件 | 覆蓋內容 |
|------|---------|---------|
| LINE 服務 | `test_line_service.py` | 訊息推播、訂單通知 |
| Firestore | `test_firestore_service.py` | 數據庫操作、會員管理 |
| 會員路由 | `test_member_routes.py` | 會員數據、訂單管理 |
| 管理員路由 | `test_admin_routes.py` | 產品管理、訂單管理 |

## 運行測試

### 使用 Shell 腳本 (Linux/Mac)
```bash
# 運行所有測試
./run_tests.sh all

# 運行單元測試
./run_tests.sh unit

# 運行整合測試
./run_tests.sh integration

# 運行測試並生成覆蓋率報告
./run_tests.sh coverage

# 快速測試
./run_tests.sh quick

# 運行特定測試文件
./run_tests.sh specific test_app.py

# 清理生成的文件
./run_tests.sh cleanup
```

### 使用 Python 腳本 (跨平台)
```bash
# 運行所有測試
python run_tests_cli.py all

# 運行單元測試
python run_tests_cli.py unit

# 運行整合測試
python run_tests_cli.py integration

# 運行測試並生成覆蓋率報告
python run_tests_cli.py coverage

# 快速測試
python run_tests_cli.py quick

# 運行特定測試文件
python run_tests_cli.py specific test_app.py

# 清理生成的文件
python run_tests_cli.py cleanup

# 顯示幫助
python run_tests_cli.py help
```

### 使用 pytest 直接運行
```bash
# 運行所有測試
pytest tests/ -v

# 運行特定測試文件
pytest tests/test_app.py -v

# 運行特定測試類
pytest tests/test_app.py::TestFlaskApp -v

# 運行特定測試方法
pytest tests/test_app.py::TestFlaskApp::test_home_route -v

# 運行測試並生成覆蓋率報告
pytest tests/ -v --cov=. --cov-report=html

# 運行測試，首次失敗時停止
pytest tests/ -v -x

# 運行測試，顯示打印輸出
pytest tests/ -v -s
```

## 覆蓋率目標

- **整體覆蓋率**: >= 80%
- **服務層覆蓋率**: >= 85%
- **路由層覆蓋率**: >= 75%
- **驗證層覆蓋率**: >= 90%

## 查看覆蓋率報告

運行覆蓋率測試後，打開 `htmlcov/index.html` 在瀏覽器中查看詳細的覆蓋率報告。

## 測試命名規範

- 測試文件: `test_*.py`
- 測試類: `Test*`
- 測試方法: `test_*`

## 撰寫新測試

### 基本單元測試模板
```python
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMyFeature(unittest.TestCase):
    """我的功能測試"""
    
    def setUp(self):
        """測試前設置"""
        pass
    
    def tearDown(self):
        """測試後清理"""
        pass
    
    def test_success_case(self):
        """測試成功情況"""
        self.assertTrue(True)
    
    def test_failure_case(self):
        """測試失敗情況"""
        self.assertFalse(False)

if __name__ == '__main__':
    unittest.main()
```

### 基本整合測試模板
```python
import unittest
import os
from unittest.mock import patch

os.environ['FLASK_ENV'] = 'testing'

class TestRoutes(unittest.TestCase):
    """路由測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        with patch('services.firestore_service.FirestoreService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    def test_route(self):
        """測試路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

## 常用斷言

```python
# 相等性測試
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# 布爾值測試
self.assertTrue(x)
self.assertFalse(x)

# 身份測試
self.assertIs(a, b)
self.assertIsNot(a, b)

# 容器測試
self.assertIn(a, b)
self.assertNotIn(a, b)

# 型別測試
self.assertIsInstance(a, type)
self.assertIsNotInstance(a, type)

# 例外測試
with self.assertRaises(ValueError):
    function_that_raises()

# 異常情況
self.assertIsNone(x)
self.assertIsNotNone(x)
```

## CI/CD 整合

### GitHub Actions 示例
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: python run_tests_cli.py coverage
```

## 故障排除

### 問題：導入模塊失敗
**解決方案**：確保 `sys.path.insert(0, ...)` 在測試文件的頂部

### 問題：測試超時
**解決方案**：檢查是否有無限循環或阻塞操作

### 問題：測試環境設置失敗
**解決方案**：確保虛擬環境已激活，所有依賴已安裝

## 下一步改進

- [ ] 增加 API 認證測試
- [ ] 增加數據庫交易測試
- [ ] 增加性能測試
- [ ] 增加安全性測試
- [ ] 集成到 CI/CD 流水線
