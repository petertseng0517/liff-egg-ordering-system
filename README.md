# 🐔 土雞蛋訂購與管理系統 (LINE LIFF + Flask + Google Sheets)

這是一個專為農產品銷售設計的完整解決方案，結合了 LINE LIFF 的便捷性、Python Flask 的強大後端邏輯，以及 Google Sheets 作為輕量級資料庫的靈活性。系統包含**客戶端訂購介面**與**管理員專屬後台**，支援分批出貨管理與自動化 LINE 通知。

## ✨ 核心功能

### 📱 客戶端 (LINE LIFF)
*   **會員註冊**：
    *   自動綁定 LINE 帳號。
    *   填寫姓名、電話、**出生日期**。
    *   支援 **雙配送地址** 設定。
*   **商品訂購**：
    *   直觀的商品選擇與數量調整。
    *   **優惠組自動轉換**：選擇「11盤優惠組」，系統自動記錄為 11 盤，確保庫存與出貨計算正確。
*   **訂購紀錄查詢**：
    *   即時查看歷史訂單狀態。
    *   顯示詳細資訊：日期、商品內容、金額。
    *   **新增付款狀態顯示**：清楚標示「未付款」、「已付款」等狀態。
*   **即時通知**：
    *   下單成功後，自動收到 LINE 確認訊息。
    *   出貨或狀態變更時，自動收到進度通知。

### 💻 管理員後台 (/admin)
*   **安全登入**：
    *   具備密碼保護的登入機制，確保資料安全。
*   **訂單總覽**：
    *   支援依日期 (今日/本週/本月)、訂單狀態篩選。
    *   關鍵字搜尋 (訂單號、姓名、電話)。
    *   直觀的狀態標籤 (物流狀態 + 付款狀態)。
*   **分批出貨管理 (Partial Delivery)**：
    *   針對農產品特性設計，支援單筆訂單分多次出貨。
    *   **出貨進度條**：視覺化顯示已出貨盤數與剩餘盤數。
    *   **防呆機制**：輸入數量超過剩餘量時自動阻擋。
    *   **自動狀態更新**：
        *   出貨量 < 訂購量 -> 自動轉為「部分配送」。
        *   出貨量 = 訂購量 -> 自動轉為「已完成」。
*   **金流管理**：
    *   獨立的 **付款狀態 (PaymentStatus)** 欄位。
    *   可手動標記「已付款」、「退款中」等，與物流狀態解耦。

## 🛠️ 技術架構

*   **前端**: HTML5, CSS (Bootstrap 5), JavaScript, LINE LIFF SDK
*   **後端**: Python 3.x, Flask
*   **資料庫**: Google Sheets (透過 gspread API)
*   **通訊**: LINE Messaging API (Push Message)
*   **部署**: 支援 Render 或其他雲端平台

## 🚀 快速開始

### 1. 環境設定
建立 `.env` 檔案以存放敏感資訊：
```env
# LINE Messaging API 設定
LINE_CHANNEL_ACCESS_TOKEN=你的_CHANNEL_ACCESS_TOKEN

# Google Sheets 設定
SPREADSHEET_ID=你的試算表ID

# 系統安全設定
FLASK_SECRET_KEY=請設定一個隨機亂碼
ADMIN_PASSWORD=設定你的後台登入密碼
```

### 2. Google Sheets 結構
請在試算表中建立兩個工作表，並設定首列標題：

**`Members` 工作表**
| A | B | C | D | E | F |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UserId | Name | Phone | Address | BirthDate | Address2 |

**`Orders` 工作表**
| A | B | C | D | E | F | G | H |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| OrderId | UserId | Item | Amount | Date | Status | DeliveryLogs | PaymentStatus |

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 啟動服務
```bash
python app.py
```
*   前台入口：`http://localhost:5000/`
*   後台入口：`http://localhost:5000/admin`

## 📦 部署指南 (Render)

1.  將程式碼推送到 GitHub。
2.  在 Render 建立 Web Service。
3.  **Environment Variables**：將 `.env` 中的內容設定到 Render 的環境變數中。
4.  **Secret Files**：上傳 `service_account.json`。
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `gunicorn app:app`

## 📝 版本紀錄

*   **v2.0 (最新)**
    *   新增管理員登入驗證。
    *   新增分批出貨管理功能。
    *   新增付款狀態欄位與管理。
    *   優化商品數量正規化邏輯。
    *   強化 LINE 自動通知機制。
    *   安全性升級 (環境變數隔離)。
*   **v1.0**
    *   基本訂購、註冊、歷史紀錄功能。

---
由 Gemini Agent 協助開發