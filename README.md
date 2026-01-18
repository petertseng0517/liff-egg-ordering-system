# 🐔 土雞蛋訂購與管理系統 
## (LINE LIFF + Flask + Firestore + ECPay)

**介紹影片**：[點擊觀看](https://www.youtube.com/watch?v=t_SznU7OYNU)

這是一個**生產級農產品訂購系統**，專為田間直銷設計。整合 LINE 通訊便捷性、Python Flask 穩定後端、Firebase Firestore 實時資料庫與綠界金流安全支付，提供**完整的線上訂購、金流整合、分批出貨、出貨修正、審計追蹤與報表系統**的一站式解決方案。

---

## 📊 系統特色

| 特色 | 說明 |
|------|------|
| **LINE LIFF 整合** | 用戶無需下載 APP，直接透過 LINE 訂購，自動綁定會員 |
| **完整金流支持** | 信用卡、ATM 轉帳、LINE Pay、銀行轉帳、貨到付款全覆蓋 |
| **分批出貨管理** | 針對農產品特性，支援單筆訂單分多次出貨，每次獨立設定出貨日期 |
| **出貨修正機制** | 完整的修正功能，可修改出貨數量、地點、日期，系統自動記錄修正歷史 |
| **審計追蹤系統** | 完整記錄所有修正操作（修改者、時間、前值、後值、原因），支援數據追溯 |
| **報表系統** | 出貨單報表，按日期查詢所有出貨紀錄，支援 Excel 匯出 |
| **實時通知系統** | 訂單、付款、出貨狀態自動推播 LINE 訊息通知 |
| **響應式設計** | 後台支援桌面表格與手機卡片檢視 |
| **企業級安全** | 300 秒會話超時、多帳號管理、密碼限制、IP 追蹤與速率控制 |
| **Firestore 資料庫** | 雲端無伺服器方案，實時同步，自動備份，支援複雜查詢 |

---

## ✨ 核心功能清單

### 👥 客戶端 (LINE LIFF 購物平台)

#### 會員系統
- **自動綁定**：LINE 帳號一鍵登入，無需記密碼
- **資料管理**：
  - 姓名、電話、出生日期
  - **雙配送地址**支援（家、公司等多地址）
  - 已註冊會員可自行編輯資料，系統預填舊資料加速修改
- **數據完整性**：電話號碼自動以文本格式存儲，前導零不遺失

#### 商品訂購與支付
- **優惠組自動換算**
  - 訂購「土雞蛋1盤」支援批量優惠：
    - 1-9盤：$250/盤
    - 10-19盤：$240/盤
    - 20盤以上：$230/盤
  - 選擇「11盤優惠組」自動記錄為 11 盤
  
- **多元付款方式**
  - **線上支付（ECPay）**：信用卡、ATM 虛擬帳號、LINE Pay（生產級支援）
  - **傳統支付**：銀行轉帳、貨到付款
  - **自動對帳**：綠界支付成功即時更新訂單狀態為「已付款」

#### 訂單管理
- 即時查詢歷史訂單與詳細狀態
- 清晰顯示：下單日期、商品數量、金額、出貨進度
- **付款資訊面板**：狀態 + 付款方式一目瞭然

#### 實時通知
- ✅ 下單成功確認
- ✅ 付款成功推播（自動或手動支付都支援）
- ✅ 出貨狀態更新與配送地點確認
- ✅ 訂單完成通知

---

### 🔧 管理員後台 (`/admin`)

#### 安全與權限
- **多帳號管理**：支援多個管理員帳號在環境變數中設定
- **會話安全**
  - 無操作 **300 秒** (5分鐘) 自動登出
  - 失敗登入次數限制（5 次後鎖定 5 分鐘）
  - IP 地址追蹤防暴力破解
- **訪問控制**：非管理員自動導向登入頁

#### 訂單管理與查詢
- **靈活篩選**：
  - 日期範圍篩選（今日/本週/本月）
  - 訂單狀態篩選
  - 付款狀態篩選
  - 關鍵字搜尋（會員名、電話、訂單號）
  
- **直觀展示**
  - 物流狀態標籤（待出貨/配送中/已完成）
  - 付款狀態標籤（未付款/已付款）
  - **付款方式欄位**：一眼辨識線上還是線下支付
  
- **響應式設計**
  - 桌面版：完整資料表格
  - 手機版：卡片式檢視，操作不受限

#### 會員資料管理
- 查看全部會員詳情（姓名、電話、地址）
- 直接編輯會員資料
- 修改即時同步至 Firestore

#### 分批出貨管理（Partial Delivery）✨
- **適應農產品特性**：單筆訂單支援多次分批出貨
- **出貨紀錄（增強功能）**：
  - 記錄每次出貨日期、數量、配送地點
  - 視覺化進度條（已配送 / 訂購）
  - **出貨日期欄位**：管理者可自行填寫與客戶約定的出貨日期
  - **系統時間戳記**：自動記錄紀錄產生時間（不可編輯）
  - 表格清晰顯示所有關鍵資訊
  
- **修正機制（增強版）**
  - 支援修改**出貨數量、配送地點、出貨日期**
  - 修正時確認對話清晰顯示所有修改項目
  - 修正後自動保留原始日期信息用於追蹤
  - 自動檢驗修正後總數不超過訂購數量
  
- **自動狀態更新**：已配送數量 ≥ 訂購數量時，自動標記訂單為「已完成」

#### 審計追蹤系統（Audit Trail）
- **完整操作記錄**：
  - 修正者帳號 + 時間戳記
  - 修改內容詳情（前值 → 後值），包含數量、地點、日期
  - 修正原因備註
  
- **數據完整性**：支援歷史查看與數據復原追蹤

#### 報表系統（新功能）✨
- **出貨單報表**
  - 按出貨日期查詢所有出貨紀錄
  - 顯示欄位：訂單編號、出貨數量、出貨地點、客戶姓名、客戶電話
  - 實時統計：出貨紀錄數、總出貨數量、出貨地點數
  - **Excel 匯出**：一鍵下載格式化的 Excel 報表（含統計資訊）
  - 擴展性設計，預留位置供後續報表類型（銷售報表、庫存報表等）

#### 金流管理
- **自動對帳**：綠界線上支付成功自動更新
- **手動管理**：亦可手動標記付款狀態
- **物流解耦**：付款與出貨狀態獨立管理

---

## 🛠️ 技術棧

| 層級 | 技術 | 說明 |
|------|------|------|
| **前端** | HTML5, CSS3, JavaScript | Bootstrap 5 響應式框架，原生 JS 無重型依賴 |
| **LINE 整合** | LINE LIFF SDK, LINE Messaging API | 前端 LIFF UI + 後端推播通知 |
| **後端** | Python 3.x, Flask | 輕量級框架，模組化藍圖結構 |
| **資料庫** | Firebase Firestore | 實時雲端資料庫，自動同步，支援複雜查詢 |
| **金流** | ECPay SDK (綠界) | 生產級支付整合，Server-to-Server 自動對帳 |
| **驗證** | LINE Messaging API | 自動會員綁定與身份驗證 |
| **部署** | Render, Heroku | 一鍵部署，自動 HTTPS 與環境變數管理 |
| **Excel 匯出** | XLSX.js | 客戶端 Excel 生成，無需伺服器依賴 |
| **測試** | pytest, unittest-xml-reporting | 52+ 項單元測試保證穩定性 |

### 📁 程式結構
```
ai_eggs/
├── app.py                          # 應用入口，路由註冊
├── config.py                       # 全局配置管理 (含 SESSION_TIMEOUT 設定)
├── auth.py                         # 登入速率限制與防暴力
├── validation.py                   # 資料驗證邏輯
│
├── routes/                         # 藍圖模組
│   ├── auth.py                    # 登入/登出
│   ├── member.py                  # 會員註冊/編輯
│   ├── admin.py                   # 後台核心邏輯 + 報表 API
│   └── ecpay.py                   # 金流回調處理
│
├── services/                       # 業務邏輯層
│   ├── database_adapter.py        # 資料庫適配器
│   ├── firestore_service.py       # Firestore 操作
│   ├── google_sheets.py           # Google Sheets 操作 (備用)
│   └── line_service.py            # LINE 推播通知
│
├── templates/                      # 前端模板
│   ├── index.html                 # 首頁（訂購界面）
│   ├── login.html                 # 後台登入
│   ├── admin.html                 # 後台訂單管理主介面
│   ├── admin_reports.html         # 報表系統介面 ✨ 新增
│   ├── admin_products.html        # 商品管理
│   ├── admin_settings.html        # 系統設定（分類、折扣、警告）
│   └── admin_old.html             # 舊版後台（保留）
│
├── tests/                          # 單元測試
│   ├── test_app.py                # 應用測試
│   ├── test_auth.py               # 驗證測試
│   ├── test_validation.py         # 驗證邏輯測試
│   └── ...
│
├── requirements.txt                # 依賴清單
└── README.md                       # 本檔案
```

---

## 📋 預置環境變數

建立 `.env` 檔案（已包含在 `.gitignore` 中，不會被提交）：

```env
# ========== 應用基礎設定 ==========
DEBUG=False                                    # 生產環境設為 False
TIMEZONE=Asia/Taipei                           # 時區設定
USE_FIRESTORE=True                             # 使用 Firestore（True）或 Google Sheets（False）

# ========== LINE 官方帳號配置 ==========
LINE_CHANNEL_ACCESS_TOKEN=你的_CHANNEL_ACCESS_TOKEN
APP_BASE_URL=https://your-domain.onrender.com  # 務必設定公開網址供金流回調使用

# ========== Firebase Firestore 配置 ==========
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/service_account.json

# ========== 系統安全 ==========
FLASK_SECRET_KEY=請設定一個隨機亂碼（最少 32 字元）
SESSION_TIMEOUT=300                            # 無操作自動登出秒數 (5分鐘)
LOGIN_ATTEMPT_TIMEOUT=300                      # 登入失敗鎖定時間（秒）
MAX_LOGIN_ATTEMPTS=5                           # 最大登入嘗試次數

# ========== 管理員帳號（格式：帳號:密碼,帳號:密碼）==========
ADMIN_ACCOUNTS=admin:admin123,manager:manager456

# ========== 綠界金流配置 ==========
ECPAY_MERCHANT_ID=2000132                     # 測試商店代號
ECPAY_HASH_KEY=5294y06JbISpM5x9              # 測試 HashKey
ECPAY_HASH_IV=v77hoKGq4kWxNNIS               # 測試 HashIV
# 生產環境須替換為真實商家資訊
```

> ⚠️ **安全提示**：絕不在版本控制中提交 `.env`，線上環境使用雲端平台的環境變數管理功能

---

## 📊 Firestore 資料結構

系統使用 Firebase Firestore 作為資料庫，包含以下集合與欄位：

### Collections 結構

#### `members` - 會員集合
```javascript
{
  userId: "U1234567890...",        // LINE User ID
  name: "范國紅",
  phone: "0911351882",
  address: "新竹市...",
  address2: "台北市...",           // 備用地址
  birthDate: "1990-01-15",
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

#### `orders` - 訂單集合
```javascript
{
  orderId: "ORD20260118001",
  userId: "U1234567890...",
  items: "土雞蛋 x15",
  amount: 3500,
  status: "部分配送",              // 處理中/已確認/配送中/部分配送/已完成/已取消
  paymentStatus: "已付款",         // 未付款/已付款
  paymentMethod: "ECPay",          // 線上支付方式或傳統支付
  deliveryLogs: [                  // 出貨紀錄陣列
    {
      stamp: "2026-01-18 11:52:00",        // 系統時間戳記（自動產生）
      delivery_date: "2026-01-20",         // 與客戶約定的出貨日期（可編輯）
      qty: 10,
      corrected_qty: 10,                   // 修正後的數量（若有修正）
      address: "新竹市...",
      is_corrected: false
    }
  ],
  date: Timestamp,
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

#### `auditLogs` - 審計日誌集合
```javascript
{
  orderId: "ORD20260118001",
  operation: "update_delivery",   // 操作類型
  adminName: "admin",             // 修正者帳號
  beforeValue: {                  // 修改前
    qty: 9,
    address: "新竹市舊地址",
    delivery_date: "2026-01-19"
  },
  afterValue: {                   // 修改後
    qty: 10,
    address: "新竹市新地址",
    delivery_date: "2026-01-20"
  },
  reason: "客戶要求修改地點",
  timestamp: Timestamp
}
```

#### 其他集合
- `products` - 商品資訊
- `stockLogs` - 庫存異動紀錄
- `categories` - 商品分類
- `discounts` - 折扣規則
- `stockAlerts` - 庫存警告設定

---

## 🚀 快速開始

### 前置需求
- Python 3.8+
- Google 帳號（Firebase 專案）
- LINE 官方帳號（Channel ID & Access Token）
- 綠界帳號（測試商家資訊）

### Step 1：複製環境設定檔
```bash
cp .env.example .env
# 編輯 .env 並填入您的 API Keys
```

### Step 2：設定 Firebase
```bash
# 下載 service_account.json 從 Firebase Console
# 放在專案根目錄或指定的路徑
```

### Step 3：安裝依賴
```bash
pip install -r requirements.txt
```

### Step 4：本地開發環境設定

**終端機 1 - 啟動 Flask 應用**
```bash
python3 app.py
# 預設運行於 http://localhost:5005
```

**終端機 2 - 啟動 ngrok（取得公開網址）**
```bash
ngrok http 5005
# 輸出範例：https://xxxx.ngrok-free.dev
```

**更新環境變數**
```bash
# 在 .env 中設定
APP_BASE_URL=https://xxxx.ngrok-free.dev
```

**訪問應用**
- 前台：`https://xxxx.ngrok-free.dev`
- 後台：`https://xxxx.ngrok-free.dev/admin`
- 報表：`https://xxxx.ngrok-free.dev/admin/reports` ✨ 新增

### Step 5：執行測試
```bash
# 運行所有測試
pytest

# 查看覆蓋率報告
pytest --cov=routes --cov=services tests/
```

---

## 🌐 雲端部署 (Render)

### 快速部署流程

1. **推送程式碼到 GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **在 Render 建立 Web Service**
   - 連接 GitHub 倉庫
   - 選擇 main 分支

3. **配置環境變數**
   ```
   DEBUG=False
   FLASK_SECRET_KEY=隨機密鑰（32+ 字元）
   SESSION_TIMEOUT=300
   USE_FIRESTORE=True
   LINE_CHANNEL_ACCESS_TOKEN=your_token
   ADMIN_ACCOUNTS=admin:password
   ECPAY_MERCHANT_ID=2000132
   ECPAY_HASH_KEY=5294y06JbISpM5x9
   ECPAY_HASH_IV=v77hoKGq4kWxNNIS
   APP_BASE_URL=https://your-app.onrender.com
   ```

4. **上傳祕密檔案**
   - Settings → Secret Files
   - 上傳 `service_account.json`
   - 目標路徑：`/etc/secrets/service_account.json`

5. **設定啟動命令**
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app --timeout 30 --workers 1`

6. **自動部署**
   - Git 推送自動觸發
   - Render 自動重啟應用

> 💡 **提示**：Render Starter Plan (~$7/月) 確保應用不進入睡眠狀態

---

## 🔐 安全最佳實踐

✅ **必做項**
- [ ] 更改 `FLASK_SECRET_KEY` 為強隨機亂碼（32+ 字元）
- [ ] 修改預設管理員帳號密碼
- [ ] 使用 HTTPS（生產環境自動強制）
- [ ] 定期備份 Firestore 資料
- [ ] 監控異常登入嘗試

❌ **勿做項**
- ❌ 在 GitHub 提交 `.env` 檔案
- ❌ 在程式碼中硬編碼敏感資訊
- ❌ 使用弱密碼作為管理員帳號
- ❌ 在公網上暴露 Firebase 編輯權限

---

## 📈 最近更新（v3.2 - 2026-01-18）

### ✨ 新功能
- 出貨紀錄新增 **Stamp**（系統時間戳記）和 **delivery_date**（可編輯出貨日期）欄位
- **報表系統**上線 - 出貨單報表功能完整
  - 按日期查詢出貨紀錄
  - 實時統計（記錄數、總數量、地點數）
  - Excel 匯出功能
- 出貨修正功能支援修改 **出貨日期**
- 審計日誌記錄更完整（包含日期修改）

### 🔧 修改
- **會話超時**從 180 秒調整為 **300 秒**（5 分鐘）
- Firestore 資料結構優化，支援更複雜的查詢
- 前端表格隱藏 Stamp 欄位，專注於業務相關資訊

### 🐛 修正
- 修正出貨紀錄修正功能的參數傳遞問題
- 後端資料一致性檢查

---

## 💬 常見問題

**Q：如何新增管理員帳號？**

A：編輯環境變數 `ADMIN_ACCOUNTS`，格式為 `帳號:密碼,帳號:密碼`。

**Q：後台多久沒操作會自動登出？**

A：**300 秒（5 分鐘）**無操作自動登出。此值可在 `config.py` 的 `SESSION_TIMEOUT` 調整。

**Q：如何使用報表功能？**

A：登入後台 → 點擊導航欄「📊 報表管理」 → 選擇出貨日期 → 點擊「查詢」 → 檢視結果或「匯出 Excel」。

**Q：出貨紀錄可以修改哪些欄位？**

A：可修改 **出貨數量、配送地點、出貨日期**，並需填寫修正原因。系統自動記錄修正歷史。

**Q：Firestore 資料如何備份？**

A：Firebase Console 內建備份功能，或使用官方 `gcloud` 工具進行備份。

---

## 📞 聯絡支援

- **開發者**：由 AI 協助開發完成
- **問題回報**：GitHub Issues
- **技術支援**：聯絡系統管理員

---

## 📄 許可證

本專案為私有農產品銷售系統，版權歸業主所有。

---

*最後更新：2026-01-18*
