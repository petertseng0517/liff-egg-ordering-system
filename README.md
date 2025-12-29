# 🐔 土雞蛋訂購系統 (LINE LIFF + Flask + Google Sheets)

這是一個基於 LINE LIFF、Python Flask 框架和 Google Sheets API 搭建的土雞蛋訂購系統。它旨在提供一個簡單方便的平台，讓使用者可以在 LINE 中完成會員註冊、商品訂購及查詢歷史訂單。

## ✨ 主要功能

*   **會員註冊**：使用者首次進入系統可填寫姓名、電話、地址進行註冊。
*   **自動判斷會員**：已註冊會員再次進入系統時，會直接顯示歡迎頁面，無需重複填寫資料。
*   **商品訂購**：提供土雞蛋品項選擇、數量調整，並可填寫備註。
*   **訂購紀錄**：使用者可以查看自己的歷史訂單。
*   **後端儲存**：所有會員資料和訂單資料自動儲存到 Google Sheets。
*   **前端提示**：訂購或註冊成功後會顯示專屬的成功頁面。

## 🛠️ 使用技術

*   **前端**: HTML, CSS (Bootstrap), JavaScript, LINE LIFF SDK
*   **後端**: Python, Flask, gspread (Google Sheets Python API)
*   **資料庫**: Google Sheets
*   **部署**: Render, GitHub Actions (用於觸發部署)

## 🚀 本地開發與設定

### 環境準備

1.  **Python 3.x**: 確保您的系統已安裝 Python。
2.  **Git**: 用於版本控制。
3.  **虛擬環境**: 建議使用虛擬環境隔離專案依賴。

### 設定步驟

1.  **複製專案**

    ```bash
    git clone https://github.com/petertseng0517/eggs.git
    cd eggs
    ```

2.  **建立與啟用虛擬環境**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # macOS/Linux
    # .venv\Scripts\activate # Windows
    ```

3.  **安裝依賴**

    ```bash
    pip install -r requirements.txt
    ```

4.  **設定 Google Sheets API (非常重要)**

    *   前往 [Google Cloud Console](https://console.cloud.google.com/)。
    *   建立一個新專案或選擇現有專案。
    *   啟用 **"Google Sheets API"**。
    *   建立一個 **服務帳戶 (Service Account)**：
        *   導航至 "IAM & Admin" -> "Service Accounts"。
        *   點擊 "CREATE SERVICE ACCOUNT"。
        *   輸入名稱，並在步驟 2 中選擇 `Project -> Editor` 角色（或者更精確的 Sheets 編輯權限）。
        *   在步驟 3 中完成設定。
        *   建立後，點擊該服務帳戶 -> "KEYS" -> "ADD KEY" -> "Create new key" -> 選擇 `JSON` 格式 -> 點擊 "CREATE"。這將會下載 `service_account.json` 檔案。
    *   **將 `service_account.json` 檔案放置在專案的根目錄下** (與 `app.py` 同一層)。
    *   **共享 Google Sheets**：將 `service_account.json` 檔案中的 `client_email` (一串像 email 的文字) 共享到您的 Google Sheets 試算表，並給予「編輯者」權限。
    *   **更新 `app.py` 中的 `SPREADSHEET_ID`**：將 `app.py` 中的 `SPREADSHEET_ID` 變數替換為您 Google Sheets 的實際 ID (從試算表網址中複製)。
    *   **Google Sheets 試算表結構**：請確保您的 Google Sheets 試算表包含以下兩個工作表 (Sheet Name) 並有相對應的標題列：
        *   **`Members` 工作表**：
            *   `UserId` (A欄)
            *   `Name` (B欄)
            *   `Phone` (C欄)
            *   `Address` (D欄)
        *   **`Orders` 工作表**：
            *   `OrderID` (A欄)
            *   `UserId` (B欄)
            *   `Item` (C欄)
            *   `Amount` (D欄)
            *   `Date` (E欄)
            *   `Status` (F欄)

5.  **啟動 Flask 應用**

    ```bash
    python app.py
    ```
    應用程式將運行在 `http://127.0.0.1:5000/`。

### 本地測試

*   **URL 參數**：
    *   `http://127.0.0.1:5000/` (預設為會員註冊/歡迎頁)
    *   `http://127.0.0.1:5000/?page=order` (訂購頁)
    *   `http://127.0.0.1:5000/?page=history` (訂購紀錄頁)
*   **測試帳號**：在電腦瀏覽器測試時，`userId` 會自動設定為 `TEST_USER_001`。

## 🌐 部署到 Render

本專案已配置為可直接部署到 [Render](https://render.com/)。

1.  **將專案推送到 GitHub**：確保所有本地更改都已提交並推送到您的 GitHub 儲存庫的 `main` 分支。

2.  **在 Render 建立 Web Service**：
    *   登入 Render Dashboard。
    *   選擇 `New -> Web Service`。
    *   連結到您的 GitHub 儲存庫。
    *   **Name**: 您的服務名稱 (會影響 Render 提供的 URL)。
    *   **Region**: 建議選擇靠近用戶的區域 (例如 Singapore)。
    *   **Runtime**: `Python 3`。
    *   **Build Command**: `pip install -r requirements.txt` (通常會自動檢測)。
    *   **Start Command**: `gunicorn app:app` (**非常重要，請手動確認或修改**，不要使用 `python app.py`)。
    *   **Instance Type**: 選擇 `Free` (測試階段足夠)。

3.  **設定 Google Sheets Secret File**：
    *   在 Render 服務設定頁面中，找到 **"Secret Files"**。
    *   點擊 **"Add Secret File"**。
    *   **Filename**: 輸入 `service_account.json`。
    *   **File Contents**: 打開您本地的 `service_account.json` 檔案，將其**完整內容**複製並貼入此處。
    *   儲存變更。

4.  **建立 Web Service**：點擊確認建立。Render 將會自動部署您的應用程式。

## 🔗 LINE LIFF 整合

為了讓應用程式在 LINE 中正常運行並獲取真實的 LINE User ID，您需要完成以下設定：

1.  **取得 LINE LIFF ID**：
    *   前往 [LINE Developers Console](https://developers.line.biz/console/)。
    *   選擇您的 Provider 和 Channel。
    *   在左側選單點擊 **"LIFF"**，然後點擊 **"Add LIFF app"**。
    *   設定 LIFF App 的名稱、尺寸等。
    *   **Endpoint URL**：填入您在 Render 部署後獲得的 URL (例如 `https://your-service-name.onrender.com`)。
    *   儲存後，您會得到一組 **LIFF ID**。

2.  **更新專案中的 `MY_LIFF_ID`**：
    *   打開 `templates/index.html`。
    *   將 `var MY_LIFF_ID = "YOUR_LIFF_ID";` 中的 `YOUR_LIFF_ID` 替換為您在 LINE Developers Console 獲得的真實 LIFF ID。
    *   將此更改推送到 GitHub，Render 會自動重新部署。

## 🔄 持續部署 (Continuous Deployment)

*   **GitHub Actions**：本專案已配置 GitHub Actions (`.github/workflows/deploy.yml`)。
    *   每次推送到 GitHub 儲存庫的 `main` 分支時，GitHub Actions 會自動觸發一個 Workflow。
    *   此 Workflow 會向 Render 發送部署 Hook 請求，通知 Render 重新部署最新版本的應用程式。
*   **Render 自動部署**：Render 預設也會監聽 GitHub 儲存庫的變更。所以當您推送到 GitHub 時，Render 通常會自動開始部署。GitHub Actions 提供了額外的可見性與可擴展性。

## 🐞 故障排除與注意事項

*   **LIFF User ID 問題**：如果在 LINE App 內開啟時仍然顯示 `TEST_USER_001`，請檢查：
    *   LIFF ID 是否正確填寫在 `templates/index.html` 中。
    *   LINE Developers Console 中該 LIFF App 的 Endpoint URL 是否與 Render 提供的 URL 完全一致 (含 `https://`)。
    *   如果瀏覽器顯示 LIFF 相關錯誤，請檢查手機瀏覽器的開發者工具 (如有)。
*   **Render 免費方案**：Render 的免費 Web Service 會在閒置 15 分鐘後進入休眠。第一次訪問時會有約 30-50 秒的喚醒時間。
*   **Google Sheets 權限**：確保服務帳戶的 `client_email` 已被共享到 Google Sheets 試算表，並擁有編輯權限。

---
希望這份 README 文件對您有所幫助！
