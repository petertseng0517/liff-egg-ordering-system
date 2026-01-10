# 🐔 土雞蛋訂購與管理系統 
## (LINE LIFF + Flask + Google Sheets + ECPay)

**介紹影片**：[點擊觀看](https://www.youtube.com/watch?v=t_SznU7OYNU)

這是一個**生產級農產品訂購系統**，專為田間直銷設計。整合 LINE 通訊便捷性、Python Flask 穩定後端、Google Sheets 靈活資料管理與綠界金流安全支付，提供**完整的線上訂購、金流整合、分批出貨與自動通知**的一站式解決方案。

## 📊 系統特色

| 特色 | 說明 |
|------|------|
| **LINE LIFF 整合** | 用戶無需下載 APP，直接透過 LINE 訂購，自動綁定會員 |
| **完整金流支持** | 信用卡、ATM 轉帳、LINE Pay、銀行轉帳、貨到付款全覆蓋 |
| **分批出貨管理** | 針對農產品特性，支援單筆訂單分多次出貨並自動狀態更新 |
| **審計追蹤** | 完整記錄所有出貨修正操作，支援數據修復與復查 |
| **實時通知系統** | 訂單、付款、出貨狀態自動推播 LINE 訊息通知 |
| **響應式設計** | 後台支援桌面表格與手機卡片檢視 |
| **企業級安全** | 180秒會話超時、多帳號管理、密碼限制與速率控制 |
| **無伺服器資料庫** | Google Sheets API，易於備份與匯出，維護成本極低 |

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
  - 無操作 180 秒自動登出
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
- 修改即時同步至 Google Sheets

#### 分批出貨管理（Partial Delivery）
- **適應農產品特性**：單筆訂單支援多次分批出貨
- **出貨紀錄**：
  - 記錄每次出貨日期、數量、配送地點
  - 視覺化進度條（已配送 / 訂購）
  
- **修正機制**
  - 支援修改歷史出貨數量與配送地點
  - 一鍵快速修正，無需重新輸入
  
- **自動狀態更新**：已配送數量 ≥ 訂購數量時，自動標記訂單為「已完成」

#### 審計追蹤系統（Audit Trail）
- **完整操作記錄**：
  - 修正者帳號 + 時間戳記
  - 修改內容詳情（前值 → 後值）
  - 修正原因備註
  
- **數據完整性**：支援歷史查看與數據復原追蹤

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
| **資料庫** | Google Sheets + gspread API | 無伺服器方案，易於備份與權限管理 |
| **金流** | ECPay SDK (綠界) | 生產級支付整合，Server-to-Server 自動對帳 |
| **驗證** | LINE Messaging API | 自動會員綁定與身份驗證 |
| **部署** | Render, Heroku | 一鍵部署，自動 HTTPS 與環境變數管理 |
| **測試** | pytest, unittest-xml-reporting | 52 項單元測試保證穩定性 |

### 📁 程式結構
```
ai_eggs/
├── app.py                          # 應用入口，路由註冊
├── config.py                       # 全局配置管理
├── auth.py                         # 登入速率限制與防暴力
├── validation.py                   # 資料驗證邏輯
│
├── routes/                         # 藍圖模組
│   ├── auth.py                    # 登入/登出
│   ├── member.py                  # 會員註冊/編輯
│   ├── admin.py                   # 後台核心邏輯
│   └── ecpay.py                   # 金流回調處理
│
├── services/                       # 業務邏輯層
│   ├── google_sheets.py           # Google Sheets 操作
│   └── line_service.py            # LINE 推播通知
│
├── templates/                      # 前端模板
│   ├── index.html                 # 首頁（訂購界面）
│   ├── login.html                 # 後台登入
│   ├── admin.html                 # 後台主介面
│   └── admin_old.html             # 舊版後台（保留）
│
├── tests/                          # 單元測試
│   ├── test_app.py                # 應用測試
│   ├── test_auth.py               # 驗證測試
│   ├── test_validation.py         # 驗證邏輯測試
│   └── ...
│
└── requirements.txt                # 依賴清單
```

## � 預置環境變數

建立 `.env` 檔案（已包含在 `.gitignore` 中，不會被提交）：

```env
# ========== 應用基礎設定 ==========
DEBUG=False                                    # 生產環境設為 False
TIMEZONE=Asia/Taipei                           # 時區設定

# ========== LINE 官方帳號配置 ==========
LINE_CHANNEL_ACCESS_TOKEN=你的_CHANNEL_ACCESS_TOKEN
APP_BASE_URL=https://your-domain.onrender.com  # 務必設定公開網址供金流回調使用

# ========== Google Sheets 配置 ==========
SPREADSHEET_ID=你的試算表ID

# ========== 系統安全 ==========
FLASK_SECRET_KEY=請設定一個隨機亂碼（最少 32 字元）
SESSION_TIMEOUT=180                            # 無操作自動登出秒數

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

## 📊 Google Sheets 資料結構

系統使用 Google Sheets 作為資料庫，請預先建立以下工作表與欄位：

### `Members` 工作表（會員）
| A | B | C | D | E | F |
|:---:|:---:|:---:|:---:|:---:|:---:|
| UserId | Name | Phone | Address | BirthDate | Address2 |
| 12345 | 王小明 | 0912345678 | 台北市... | 1990-01-15 | 新竹市... |

### `Orders` 工作表（訂單）
| A | B | C | D | E | F | G | H | I |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| OrderId | UserId | Item | Amount | Date | Status | DeliveryLogs | PaymentStatus | PaymentMethod |
| ORD001 | 12345 | 土雞蛋 | 2 | 2026-01-10 | 已完成 | [配送紀錄] | 已付款 | 綠界 |

### `DeliveryAuditLog` 工作表（審計日誌）
| A | B | C | D | E | F | G | H |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 時間戳記 | 訂單編號 | 操作類型 | 管理者帳號 | 修改前數值 | 修改後數值 | 原因 | 備註 |
| 2026-01-10 14:30 | ORD001 | 出貨修正 | admin | 2 | 3 | 補貨 | 客戶追加 |

> **新安裝提示**：`DeliveryAuditLog` 工作表需**手動在 Google Sheets 中建立**

---

## 🚀 快速開始

### 前置需求
- Python 3.8+
- Google 帳號（申請 OAuth 認證）
- LINE 官方帳號（申請 Channel ID & Access Token）
- 綠界帳號（取得測試商家資訊）

### Step 1：複製環境設定檔
```bash
cp .env.example .env
# 編輯 .env 並填入您的 API Keys 與 Google Sheets ID
```

### Step 2：安裝依賴
```bash
pip install -r requirements.txt
```

### Step 3：本地開發環境設定

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

# 或在啟動 Flask 時傳入
APP_BASE_URL=https://xxxx.ngrok-free.dev python3 app.py
```

**訪問應用**
- 前台：`https://xxxx.ngrok-free.dev`
- 後台：`https://xxxx.ngrok-free.dev/admin`

### Step 4：執行測試
```bash
# 運行所有測試
pytest

# 查看覆蓋率報告
pytest --cov=routes --cov=services tests/

# 輸出 XML 測試報告
pytest --junit-xml=test-results.xml
```

---

## 🌐 Render 雲端部署

### 自動部署流程

1. **將程式碼推送到 GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **在 Render 建立新的 Web Service**
   - 連接你的 GitHub 倉庫
   - 選擇 main 分支

3. **配置環境變數**（Render Dashboard → Settings → Environment）
   ```
   DEBUG=False
   FLASK_SECRET_KEY=你的_隨機密鑰
   LINE_CHANNEL_ACCESS_TOKEN=你的_TOKEN
   SPREADSHEET_ID=你的_SHEETS_ID
   ADMIN_ACCOUNTS=admin:密碼
   ECPAY_MERCHANT_ID=2000132
   ECPAY_HASH_KEY=5294y06JbISpM5x9
   ECPAY_HASH_IV=v77hoKGq4kWxNNIS
   APP_BASE_URL=https://your-app.onrender.com
   ```

4. **上傳祕密檔案**（Render 不支援環境變數上傳大檔案）
   - Settings → Secret Files → 上傳 `service_account.json`
   - 設定目標路徑為 `/etc/secrets/service_account.json`
   - 在 `config.py` 中引用此路徑

5. **設定啟動命令**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --timeout 30 --workers 1`

6. **自動部署**
   - Git 推送自動觸發部署
   - Render 會自動重新啟動應用

> 💡 **提示**：Render Starter Plan (約 $7/月) 確保應用不會進入睡眠狀態，用戶隨點隨用

---

## � 常見問題 & 故障排除

### ❓ 管理員與安全

**Q1：如何新增/修改管理員帳號？**

A：編輯環境變數 `ADMIN_ACCOUNTS`：
```
admin:admin123,manager:manager456,owner:owner789
```
修改後自動重新部署生效。Render 會自動重啟應用。

**Q2：為什麼被鎖定 5 分鐘？**

A：連續登入失敗 5 次後，系統自動鎖定該 IP 5 分鐘以防暴力攻擊。清除 Cookies 或更換網路可重試。

**Q3：後台自動登出？**

A：180 秒無操作自動登出是安全設計。請重新登入。

---

### ❓ 會員與訂購

**Q4：為什麼會員編輯資料後看不到變更？**

A：
1. 確認已點擊「保存變更」按鈕
2. 重新整理頁面（Ctrl+F5 強制刷新）
3. 檢查 Google Sheets 是否已同步
4. 若仍無更新，聯絡系統管理員

**Q5：訂單狀態為什麼一直是「待出貨」？**

A：
1. 檢查出貨紀錄中的數字是否正確輸入
2. 確保「已配送」數量 ≥ 「訂購」數量時才會自動更新為「已完成」
3. 若數字正確但狀態未更新，重啟應用或手動修改

**Q6：訂購後沒有收到 LINE 通知？**

A：
1. 確認 LINE 官方帳號已正確設定
2. 檢查 LINE 聊天室是否有訊息（可能在垃圾箱）
3. 後台日誌檢查 LINE API 回應錯誤
4. 確保 `LINE_CHANNEL_ACCESS_TOKEN` 有效

---

### ❓ 出貨與金流

**Q7：如何修正出貨紀錄？**

A：
1. 進入管理後台 → 找到訂單
2. 點擊「修正」按鈕
3. 修改出貨數量與配送地點
4. 系統自動記錄修正操作到審計日誌

**Q8：綠界線上支付為什麼無法完成？**

A：
1. 確認現在使用的是**測試環境商家資訊**（MERCHANT_ID=2000132）
2. 測試環境信用卡號：4111111111111111（任意密碼與月年）
3. 線上測試前清除瀏覽器 Cookies
4. Render 部署時確保 `APP_BASE_URL` 設為正確的網址

**Q9：綠界回調（Callback）沒有成功？**

A：
1. 檢查 `APP_BASE_URL` 環境變數是否為外部可訪問的 HTTPS 網址
2. 本地開發務必使用 ngrok 提供的公開 URL
3. 確保 `/ecpay/callback` 路由存在且無驗證限制
4. 檢查 Render 日誌是否有 POST 請求錯誤

---

### ❓ 技術與部署

**Q10：本地開發時 ngrok URL 變更怎麼辦？**

A：ngrok 每次重啟都會生成新 URL。請在 `.env` 中更新 `APP_BASE_URL`，或直接在啟動 Flask 時傳入環境變數。

**Q11：Google Sheets API 達到配額限制？**

A：
1. 免費帳號每天請求數有限
2. 考慮升級 Google Workspace
3. 優化程式邏輯減少 API 呼叫（例如批次更新）
4. 聯絡開發者討論最佳化方案

**Q12：系統支援多少訂單？**

A：
- Google Sheets 單工作表上限 **5,000,000 行**
- LINE Messaging API 免費方案支援 **500 則群發訊息/月**（約 150 訂單）
- 超過需升級 LINE 官方帳號到中用量方案（NT$800/月）

---

## 🔐 安全最佳實踐

✅ **必做項**
- [ ] 更改 `FLASK_SECRET_KEY` 為強隨機亂碼（32+ 字元）
- [ ] 修改預設管理員帳號密碼
- [ ] 使用 HTTPS（生產環境自動強制）
- [ ] 定期備份 Google Sheets 資料
- [ ] 啟用 Google Sheets 的版本歷史功能

❌ **勿做項**
- ❌ 在 GitHub 提交 `.env` 檔案
- ❌ 在程式碼中硬編碼敏感資訊
- ❌ 使用弱密碼作為管理員帳號
- ❌ 在公網上暴露 Google Sheets 編輯權限

---

## 📊 系統規格與效能

| 指標 | 數值 | 備註 |
|------|------|------|
| **並發用戶** | ~50-100 | Render Starter Plan |
| **請求延遲** | 200-500ms | Google Sheets API |
| **資料庫容量** | 500MB+ | 單個 Google Sheets |
| **月費成本** | ~NT$230-800 | Render + LINE 方案 |
| **上線時間** | ~99% | 排除計畫維護 |
| **自動備份** | ✅ | Google Sheets 版本控制 |

---

## 📜 版本歷史

| 版本 | 日期 | 重要更新 |
|------|------|--------|
| **v3.1** (生產版) | 2026-01-07 | ✨ 會員自服務編輯、出貨地點追蹤、審計日誌、會話超時、多帳號管理 |
| **v3.0** | 2025-11-15 | 🏦 ECPay 金流整合、自動對帳、響應式設計 |
| **v2.0** | 2025-09-20 | 🔐 管理員驗證、分批出貨、付款狀態欄位 |
| **v1.0** | 2025-07-01 | 📱 基礎訂購、LINE 會員、訂單紀錄 |

---

## 📧 聯絡與支援

- **開發者**：由 AI 協助開發完成
- **問題回報**：請在 GitHub 上提交 Issue
- **功能請求**：歡迎討論與建議改進
- **技術支援**：聯絡系統管理員

---

## 📄 許可證

本專案為私有農產品銷售系統，版權歸業主所有。

---

## 🙏 致謝

感謝以下服務提供支持：
- 🟢 **LINE** - 官方帳號與 LIFF SDK
- 📊 **Google Sheets** - 輕量級資料管理
- 🏦 **ECPay 綠界科技** - 安全金流整合
- ☁️ **Render** - 穩定雲端部署
- 🔵 **Flask** - 優雅的後端框架

---

*最後更新：2026-01-10*