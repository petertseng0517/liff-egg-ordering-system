# 蛋雞訂單管理系統 - 單元測試使用指南

## 快速開始

### 安裝依賴
```bash
# 激活虛擬環境
source .venv/bin/activate

# 安裝測試依賴（如果還未安裝）
pip install pytest pytest-cov
```

### 運行測試

#### 方式1: 使用 Python CLI 工具（推薦）
```bash
# 運行所有測試
python run_tests_cli.py all

# 運行快速測試
python run_tests_cli.py quick

# 運行單元測試
python run_tests_cli.py unit

# 運行整合測試
python run_tests_cli.py integration

# 生成覆蓋率報告
python run_tests_cli.py coverage

# 清理測試文件
python run_tests_cli.py cleanup
```

#### 方式2: 使用 Shell 腳本 (Linux/Mac)
```bash
# 運行所有測試
./run_tests.sh all

# 運行單元測試
./run_tests.sh unit

# 運行整合測試
./run_tests.sh integration

# 生成覆蓋率報告
./run_tests.sh coverage
```

#### 方式3: 直接使用 pytest
```bash
# 運行所有測試
pytest tests/ -v

# 運行特定文件
pytest tests/test_auth.py -v

# 運行特定類
pytest tests/test_auth.py::TestPasswordManager -v

# 運行特定方法
pytest tests/test_auth.py::TestPasswordManager::test_hash_password -v

# 生成覆蓋率報告
pytest tests/ --cov=. --cov-report=html

# 首次失敗時停止
pytest tests/ -x

# 顯示打印輸出
pytest tests/ -s
```

## 測試文件結構

```
tests/
├── __init__.py
├── test_auth.py                 # 認證和密碼管理測試
├── test_config.py               # 產品配置測試
├── test_validation.py           # 表單驗證測試
├── test_app.py                  # Flask 應用測試
├── test_delivery.py             # 配送邏輯測試
├── test_delivery_validation.py  # 配送驗證測試
├── test_message_format.py       # 訊息格式測試
├── test_line_service.py         # LINE 訊息服務測試 ★ 新
├── test_firestore_service.py    # Firestore 服務測試 ★ 新
├── test_member_routes.py        # 會員路由測試 ★ 新
└── test_admin_routes.py         # 管理員路由測試 ★ 新
```

## 最近的改進 (2026-01-18)

### 新增 4 個測試文件

#### 1️⃣ test_line_service.py
測試 LINE 訊息推播服務
- ✅ 訊息推送
- ✅ 訂單通知
- ✅ 支付通知
- ✅ 配送通知
- ✅ 錯誤處理

**執行**: `pytest tests/test_line_service.py -v`

#### 2️⃣ test_firestore_service.py
測試 Firebase Firestore 服務
- ✅ 初始化
- ✅ 會員操作 (新增、查詢、更新)
- ✅ 訂單操作 (新增、查詢、更新)
- ✅ 配送紀錄管理

**執行**: `pytest tests/test_firestore_service.py -v`

#### 3️⃣ test_member_routes.py
測試會員相關路由
- ✅ 會員頁面訪問
- ✅ 下單頁面訪問
- ✅ 會員資料驗證
- ✅ 電話號碼驗證

**執行**: `pytest tests/test_member_routes.py -v`

#### 4️⃣ test_admin_routes.py
測試管理員相關路由
- ✅ 產品管理 (新增、更新、刪除)
- ✅ 訂單管理
- ✅ 分類管理
- ✅ 權限驗證

**執行**: `pytest tests/test_admin_routes.py -v`

### 測試統計

| 指標 | 數值 |
|------|------|
| 總測試數 | 139 |
| 通過數 | 134 |
| 失敗數 | 5 |
| 成功率 | **96.4%** |
| 新增測試 | 30 |
| 代碼覆蓋率 | 49% |

## 查看覆蓋率報告

運行覆蓋率測試後：

```bash
python run_tests_cli.py coverage
```

然後在瀏覽器中打開 `htmlcov/index.html`

## 編寫新測試

### 基本單元測試模板

```python
import unittest
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module import MyClass

class TestMyClass(unittest.TestCase):
    """測試類描述"""
    
    def setUp(self):
        """測試前設置 - 每個測試方法前執行"""
        self.instance = MyClass()
    
    def tearDown(self):
        """測試後清理 - 每個測試方法後執行"""
        pass
    
    def test_success_case(self):
        """測試成功情況"""
        result = self.instance.method()
        self.assertEqual(result, expected_value)
    
    def test_failure_case(self):
        """測試失敗情況"""
        with self.assertRaises(ValueError):
            self.instance.invalid_method()

if __name__ == '__main__':
    unittest.main()
```

### 基本整合測試模板

```python
import unittest
import os
from unittest.mock import patch

# 設定測試環境
os.environ['FLASK_ENV'] = 'testing'

class TestRoutes(unittest.TestCase):
    """路由整合測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化 - 所有測試方法前執行一次"""
        with patch('services.firestore_service.FirestoreService.init'):
            from app import app
            cls.app = app
            cls.client = app.test_client()
    
    def test_home_page(self):
        """測試首頁路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

## 常見問題

### Q: 如何只運行某個模塊的測試？
A: 
```bash
pytest tests/test_auth.py -v
```

### Q: 如何運行某個特定的測試方法？
A:
```bash
pytest tests/test_auth.py::TestPasswordManager::test_hash_password -v
```

### Q: 如何生成 HTML 覆蓋率報告？
A:
```bash
pytest tests/ --cov=. --cov-report=html
# 然後打開 htmlcov/index.html
```

### Q: 測試太慢怎麼辦？
A: 使用並行運行（需要安裝 pytest-xdist）：
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### Q: 如何只看失敗的測試？
A:
```bash
pytest tests/ --lf  # 運行上次失敗的測試
pytest tests/ --ff  # 先運行失敗的，再運行通過的
```

### Q: 如何看到所有的打印語句？
A:
```bash
pytest tests/ -s
```

## 故障排除

### 問題：導入模塊失敗
**解決**：確保虛擬環境已激活
```bash
source .venv/bin/activate
```

### 問題：pytest 命令未找到
**解決**：安裝 pytest
```bash
pip install pytest pytest-cov
```

### 問題：測試超時
**解決**：檢查是否有無限循環或 I/O 阻塞

### 問題：覆蓋率報告未生成
**解決**：確保安裝了 pytest-cov
```bash
pip install pytest-cov
```

## 最佳實踐

### ✅ 做這些

1. **編寫清晰的測試名稱**
   ```python
   def test_validate_register_form_with_empty_name(self):  # ✅ 好
       pass
   ```

2. **為每個測試添加文檔字符串**
   ```python
   def test_something(self):
       """測試具體的功能"""
       pass
   ```

3. **使用 setUp 和 tearDown 共享代碼**
   ```python
   def setUp(self):
       self.user = User(name="Test")
   ```

4. **使用 patch 模擬外部依賴**
   ```python
   @patch('services.api.call_external')
   def test_with_mock(self, mock_call):
       pass
   ```

5. **測試邊界情況**
   ```python
   def test_empty_list(self):
   def test_single_item(self):
   def test_large_list(self):
   ```

### ❌ 避免這些

1. **不要在測試間共享狀態**
   ```python
   # ❌ 不好
   class_variable = []
   ```

2. **不要測試實現細節**
   ```python
   # ❌ 不好
   self.assertEqual(obj._private_variable, value)
   ```

3. **不要使用真實的外部服務**
   ```python
   # ❌ 不好
   response = requests.get('https://api.example.com')
   ```

4. **不要使用睡眠延遲**
   ```python
   # ❌ 不好
   import time; time.sleep(1)
   ```

5. **不要忽視測試失敗**
   ```python
   # ❌ 不好
   try:
       self.fail()
   except:
       pass
   ```

## 測試覆蓋率目標

| 層級 | 目標覆蓋率 | 優先級 |
|------|----------|-------|
| 驗證層 | >= 90% | 🔴 高 |
| 服務層 | >= 85% | 🔴 高 |
| 路由層 | >= 75% | 🟡 中 |
| 整體 | >= 80% | 🟡 中 |

## 設置 Git 鉤子（可選）

自動在提交前運行測試：

```bash
# 創建 pre-commit 鉤子
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
pytest tests/ --tb=short
exit $?
EOF

chmod +x .git/hooks/pre-commit
```

## 相關文檔

- [TEST_GUIDE.md](TEST_GUIDE.md) - 詳細的測試指南
- [TEST_REPORT.md](TEST_REPORT.md) - 測試執行報告
- [pytest 官方文檔](https://docs.pytest.org/)
- [unittest 官方文檔](https://docs.python.org/3/library/unittest.html)

## 聯絡與支持

如有測試相關問題，請：

1. 查看 [TEST_GUIDE.md](TEST_GUIDE.md)
2. 查看 [TEST_REPORT.md](TEST_REPORT.md)
3. 檢查失敗的測試輸出
4. 查看相關文件的文檔字符串

---

**最後更新**: 2026-01-18  
**維護者**: Peter  
**狀態**: ✅ 正常運行 (96.4% 通過率)
