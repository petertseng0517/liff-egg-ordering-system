# 🐔 土雞蛋訂購與管理系統 - 改進文檔

本文檔說明了對原始 app.py 進行的改進和更新。

## 🔄 主要改進

### 1. **模組化結構** ✅
原始單一 app.py (543 行) 已分解為以下模組：

```
ai_eggs/
├── config.py                    # 配置管理
├── auth.py                      # 認證與密碼管理
├── validation.py                # 表單驗證
├── app.py                       # 主應用 (現在只有 ~100 行)
├── routes/
│   ├── __init__.py
│   ├── auth.py                  # 認證路由
│   ├── member.py                # 會員與訂單路由
│   ├── admin.py                 # 管理員 API
│   └── ecpay.py                 # ECPay 回調路由
├── services/
│   ├── __init__.py
│   ├── google_sheets.py         # Google Sheets 服務
│   ├── line_service.py          # LINE 訊息服務
│   └── validation.py            # 表單驗證工具
└── tests/
    ├── test_validation.py       # 驗證測試
    ├── test_auth.py             # 認證測試
    ├── test_config.py           # 配置測試
    └── test_app.py              # 應用整合測試
```

**優勢：**
- 代碼更易維護
- 功能分離清晰
- 便於單元測試
- 支援團隊協作

---

### 2. **密碼驗證與速率限制** ✅

#### 功能特性：
- ✅ **登入失敗次數限制** - 防止暴力破解
  - 最多 5 次嘗試（可配置）
  - 鎖定 300 秒（可配置）
  - 按 IP 地址追蹤

- ✅ **友善的錯誤提示**
  - 密碼強度驗證
  - 剩餘嘗試次數提示
  - 鎖定時間倒計時

#### 使用方式：
```python
from auth import login_tracker

# 在登入視圖中
if login_tracker.is_locked(client_ip):
    remaining = login_tracker.get_remaining_time(client_ip)
    return "登入嘗試過多，請在 {} 秒後重試".format(remaining)

login_tracker.record_attempt(client_ip)  # 記錄嘗試
login_tracker.reset(client_ip)           # 重置計數
```

---

### 3. **HTTPS 強制** ✅

自動強制生產環境使用 HTTPS：

```python
@app.before_request
def enforce_https():
    if not app.debug and not app.testing:
        if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
```

**支援環境：**
- ✅ Render.com
- ✅ Heroku
- ✅ AWS
- ✅ 代理後面的任何環境

---

### 4. **表單驗證與友善錯誤提示** ✅

#### 驗證工具：`validation.py`

**會員註冊驗證：**
```python
from validation import FormValidator

errors = FormValidator.validate_register_form({
    'name': 'John Doe',
    'phone': '0912345678',
    'address': '台北市',
    'birthDate': '1990-01-15'
})

if errors:
    # errors = ["姓名不能為空", "電話格式不正確", ...]
    pass
```

**訂單表單驗證：**
```python
errors = FormValidator.validate_order_form({
    'itemName': '土雞蛋1盤',
    'qty': '5',
    'paymentMethod': 'transfer',
    'remarks': '下午配送'
})
```

**驗證項目：**
- ✅ 姓名（非空，≤50 字符）
- ✅ 電話（格式驗證，10 位或 09xxxxxxxx）
- ✅ 地址（非空，≤200 字符）
- ✅ 日期（YYYY-MM-DD 格式）
- ✅ 訂單數量（1-1000）
- ✅ 備註（≤500 字符）

---

### 5. **LINE LIFF SDK 初始化說明** ✅

在 `templates/index.html` 中已添加詳細說明：

```javascript
/**
 * LINE LIFF SDK 初始化說明
 * 
 * LIFF (LINE Front-end Framework) 是 LINE 提供的前端框架
 * 讓 Web App 在 LINE 應用內運行並取得使用者信息
 * 
 * 步驟：
 * 1. 在 LINE Developers 建立 LIFF App
 * 2. 取得 LIFF ID
 * 3. 填入下面的 MY_LIFF_ID
 * 4. 部署應用並配置 LIFF URL
 * 
 * LINE 官方文檔：https://developers.line.biz/en/docs/liff/
 */

var MY_LIFF_ID = "YOUR_LIFF_ID";  // 替換為你的 LIFF ID

liff.init({ liffId: MY_LIFF_ID })
  .then(() => {
    // 取得使用者資料並初始化應用
  })
  .catch(err => {
    console.error("LIFF 初始化失敗:", err);
  });
```

**開發模式支援：**
- 在電腦瀏覽器使用測試帳號 (TEST_USER_001)
- 在 LINE App 內自動要求登入

---

### 6. **單元測試** ✅

完整的測試套件位於 `tests/` 目錄：

#### 運行測試：

```bash
# 執行所有測試
python -m unittest discover tests

# 執行特定測試
python -m unittest tests.test_validation

# 使用 pytest (推薦)
pytest tests/ -v

# 生成覆蓋率報告
pytest tests/ --cov=. --cov-report=html
```

#### 測試覆蓋範圍：

| 模組 | 測試文件 | 測試項目 |
|------|---------|---------|
| 驗證 | `test_validation.py` | 15+ 測試 |
| 認證 | `test_auth.py` | 12+ 測試 |
| 配置 | `test_config.py` | 10+ 測試 |
| 應用 | `test_app.py` | 10+ 測試 |

#### 範例測試：

```python
# 驗證電話號碼
def test_valid_phone(self):
    self.assertTrue(FormValidator._is_valid_phone('0912345678'))

# 驗證登入速率限制
def test_login_rate_limit(self):
    for i in range(5):
        tracker.record_attempt('192.168.1.1')
    self.assertTrue(tracker.is_locked('192.168.1.1'))

# 驗證產品定價
def test_bulk_pricing(self):
    price = ProductConfig.get_unit_price("土雞蛋1盤", 15)
    self.assertEqual(price, 240)  # 10-19 盤
```

---

## 📋 新增檔案清單

### 配置與工具
- `config.py` - 應用配置與產品配置
- `auth.py` - 認證、密碼管理、登入追蹤
- `validation.py` - 表單驗證

### 路由（藍圖）
- `routes/auth.py` - 登入/登出路由
- `routes/member.py` - 會員與訂單 API
- `routes/admin.py` - 管理員 API
- `routes/ecpay.py` - ECPay 回調

### 服務
- `services/google_sheets.py` - Google Sheets 操作
- `services/line_service.py` - LINE 訊息推播

### 測試
- `tests/test_validation.py` - 驗證測試
- `tests/test_auth.py` - 認證測試
- `tests/test_config.py` - 配置測試
- `tests/test_app.py` - 應用整合測試

---

## 🚀 部署與運行

### 開發環境

```bash
# 安裝依賴
pip install -r requirements.txt

# 設置環境變數
export FLASK_SECRET_KEY="your-secret-key"
export ADMIN_PASSWORD="your-password"
export SPREADSHEET_ID="your-sheet-id"
export LINE_CHANNEL_ACCESS_TOKEN="your-token"

# 運行應用
python app.py

# 運行測試
python -m unittest discover tests
```

### 生產環境（Render）

```bash
# .env 文件配置
APP_BASE_URL=https://your-app.onrender.com
FLASK_SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-password
SPREADSHEET_ID=your-sheet-id
LINE_CHANNEL_ACCESS_TOKEN=your-token

# Procfile 已配置，使用 gunicorn 運行
```

---

## 🔒 安全性改進

| 項目 | 改進 |
|------|------|
| **密碼驗證** | 登入速率限制 + 密碼強度驗證 |
| **HTTPS** | 生產環境強制 HTTPS |
| **輸入驗證** | 全面的表單驗證 |
| **日誌** | 詳細的操作日誌 |
| **配置** | 敏感信息使用環境變數 |

---

## 📊 代碼質量指標

- ✅ **模組化** - 代碼分解為小的、可測試的模塊
- ✅ **可維護性** - 清晰的代碼結構和註解
- ✅ **可測試性** - 完整的單元測試覆蓋
- ✅ **錯誤處理** - 友善的錯誤提示和日誌
- ✅ **安全性** - HTTPS、輸入驗證、速率限制

---

## 🐛 已知問題與待改進

1. **數據庫遷移**
   - 建議將 Google Sheets 遷移到真實數據庫（SQLite/PostgreSQL）
   - 提升性能和可靠性

2. **身份驗證增強**
   - 考慮使用 bcrypt 替代 PBKDF2
   - 添加 JWT token 支援

3. **監控與告警**
   - 添加應用監控
   - 設置異常告警機制

4. **API 文檔**
   - 生成 OpenAPI/Swagger 文檔
   - 簡化外部集成

---

## 📚 參考資源

- [Flask 官方文檔](https://flask.palletsprojects.com/)
- [LINE LIFF 文檔](https://developers.line.biz/en/docs/liff/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

---

## 📞 支援

如有問題或建議，請查看具體的模組文檔或運行測試獲得更多信息。

**更新日期：** 2026-01-06
