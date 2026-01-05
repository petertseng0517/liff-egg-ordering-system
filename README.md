# 🐔 土雞蛋訂購與管理系統 (LINE LIFF + Flask + Google Sheets + ECPay)
介紹影片：https://www.youtube.com/watch?v=t_SznU7OYNU
這是一個專為農產品銷售設計的完整解決方案，結合了 LINE LIFF 的便捷性、Python Flask 的強大後端邏輯、Google Sheets 作為輕量級資料庫的靈活性，以及 **綠界 (ECPay) 金流服務**。系統包含**客戶端訂購介面**與**管理員專屬後台**，支援分批出貨管理、自動化 LINE 通知與線上金流整合。

## ✨ 核心功能

### 📱 客戶端 (LINE LIFF)
*   **會員註冊**：
    *   自動綁定 LINE 帳號。
    *   填寫姓名、電話、出生日期。
    *   支援 **雙配送地址** 設定。
*   **商品訂購與支付**：
    *   直觀的商品選擇與數量調整。
    *   **土雞蛋1盤優惠方案**：訂購「土雞蛋1盤」時，單價會依數量變動 (1-9盤: $250/盤, 10-19盤: $240/盤, 20盤以上: $230/盤)。
    *   **優惠組自動轉換**：選擇「11盤優惠組」，系統自動記錄為 11 盤。
    *   **多元付款方式**：
        *   **銀行轉帳/貨到付款**：傳統線下支付模式。
        *   **線上支付 (綠界)**：支援信用卡、ATM 虛擬帳號、LINE Pay 等（目前為測試環境）。
*   **訂購紀錄查詢**：
    *   即時查看歷史訂單狀態。
    *   顯示詳細資訊：日期、商品內容、金額。
    *   **付款資訊**：清楚顯示付款狀態（如「已付款」）與付款方式（如「線上支付 (綠界)」）。
*   **即時通知**：
    *   下單成功後，自動收到 LINE 確認訊息。
    *   **付款成功通知**：線上支付完成後，即時推播確認訊息。
    *   出貨或狀態變更時，自動收到進度通知。

### 💻 管理員後台 (/admin)
*   **安全登入**：具備密碼保護的登入機制。
*   **訂單總覽**：
    *   支援依日期、訂單狀態篩選，以及關鍵字搜尋。
    *   直觀的狀態標籤 (物流狀態 + 付款狀態)。
    *   **新增「付款方式」欄位**：快速辨識訂單是透過轉帳還是綠界支付。
*   **分批出貨管理 (Partial Delivery)**：
    *   支援單筆訂單分多次出貨，視覺化顯示出貨進度。
    *   自動化狀態更新（部分配送 / 已完成）。
*   **金流管理**：
    *   **自動對帳**：綠界線上支付成功後，系統自動更新付款狀態為「已付款」。
    *   手動管理：亦可手動標記付款狀態，與物流狀態解耦。

## 🛠️ 技術架構

*   **前端**: HTML5, CSS (Bootstrap 5), JavaScript, LINE LIFF SDK
*   **後端**: Python 3.x, Flask
*   **資料庫**: Google Sheets (透過 gspread API)
*   **通訊**: LINE Messaging API (Push Message)
*   **金流**: ECPay SDK (綠界科技全方位金流)
*   **部署**: 支援 Render, Heroku 等雲端平台

## 🚀 快速開始

### 1. 環境設定
建立 `.env` 檔案以存放敏感資訊：
```env
# 應用程式基礎網址 (務必設定公開網址，供綠界回傳使用)
APP_BASE_URL=https://您的網址.onrender.com

# LINE Messaging API 設定
LINE_CHANNEL_ACCESS_TOKEN=你的_CHANNEL_ACCESS_TOKEN

# Google Sheets 設定
SPREADSHEET_ID=你的試算表ID

# 系統安全設定
FLASK_SECRET_KEY=請設定一個隨機亂碼
ADMIN_PASSWORD=設定你的後台登入密碼

# 綠界金流設定 (預設為測試環境值)
ECPAY_MERCHANT_ID=2000132
ECPAY_HASH_KEY=5294y06JbISpM5x9
ECPAY_HASH_IV=v77hoKGq4kWxNNIS
```

### 2. Google Sheets 結構
請在試算表中建立兩個工作表，並設定首列標題：

**`Members` 工作表**
| A | B | C | D | E | F |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UserId | Name | Phone | Address | BirthDate | Address2 |

**`Orders` 工作表**
| A | B | C | D | E | F | G | H | I |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| OrderId | UserId | Item | Amount | Date | Status | DeliveryLogs | PaymentStatus | **PaymentMethod** |

*(注意：需在第 9 欄新增 PaymentMethod)*

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 啟動服務
**本地開發 (使用 ngrok)**:
要啟動本地開發環境，您需要運行兩個獨立的指令：

1.  **啟動 Flask 應用程式**：
    ```bash
    python3 app.py
    ```
    此指令會啟動後端服務，通常在 `http://localhost:5000` 運行。

2.  **啟動 ngrok 以取得公開網址**：
    ```bash
    ngrok http 5000
    ```
    執行此指令後，`ngrok` 會提供一個公開的 URL (例如 `https://xxxx.ngrok-free.dev`)。請將此 URL 複製下來，並在 `.env` 檔案中設定 `APP_BASE_URL` 為此 ngrok 網址，或在啟動 Flask App 前以環境變數形式傳入。
    
    例如 (在新的終端機中運行 Flask App，並替換為您的 ngrok 網址):
    ```bash
    APP_BASE_URL=https://xxxx.ngrok-free.dev python3 app.py
    ```
*   前台入口：使用 ngrok 網址 (https://xxxx.ngrok-free.dev)
*   後台入口：https://xxxx.ngrok-free.dev/admin

## 📦 部署指南 (Render)

1.  將程式碼推送到 GitHub。
2.  在 Render 建立 Web Service。
3.  **Environment Variables**：將 `.env` 中的所有內容設定到 Render 的環境變數中，特別是 `APP_BASE_URL` 需設為 Render 提供的網址。
4.  **Secret Files**：上傳 `service_account.json`。
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `gunicorn app:app`

## 📝 版本紀錄

*   **v3.0 (最新)**
    *   **整合綠界金流 (ECPay)**：支援信用卡、ATM、LINE Pay。
    *   **自動化對帳**：實作 Server-to-Server Callback，付款成功自動更新狀態。
    *   **資料庫擴充**：新增付款方式記錄欄位。
    *   介面優化：前台與後台同步顯示詳細付款資訊。
*   **v2.0**
    *   新增管理員登入驗證、分批出貨管理、付款狀態欄位。
*   **v1.0**
    *   基本訂購、註冊、歷史紀錄功能。

---
由 Gemini Agent 協助開發