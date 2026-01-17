# Firebase Firestore 遷移指南

本文件說明如何將交易資料從 Google Sheets 遷移至 Firebase Firestore。

## 📋 前置準備

### 1. 安裝必要工具

```bash
# 安裝 Firebase CLI
npm install -g firebase-tools

# 或使用 Homebrew (macOS)
brew install firebase-cli
```

### 2. 登入 Firebase

```bash
firebase login
```

## 🔧 Firebase 專案設置

### 1. 建立或選擇 Firebase 專案

```bash
# 初始化 Firebase (會提示選擇或建立專案)
firebase init firestore
```

選擇選項：
- **選擇專案**: 建立新專案或選擇現有專案
- **Firestore 位置**: 選擇 `asia-northeast1` (日本，距離台灣最近)
- **安全規則**: 選擇開始使用 Firestore 規則
- **索引檔**: 保持預設

### 2. 下載服務帳號金鑰

1. 登入 [Firebase Console](https://console.firebase.google.com/)
2. 選擇您的專案
3. 點擊左上角的 ⚙️ (專案設定)
4. 進入 **服務帳號** 頁籤
5. 點擊 **生成新的私密金鑰**
6. 下載的 JSON 檔案包含以下資訊（設置到環境變數）：
   - `project_id` → `FIREBASE_PROJECT_ID`
   - `private_key` → `FIREBASE_PRIVATE_KEY`
   - `client_email` → `FIREBASE_CLIENT_EMAIL`
   - `client_id` → `FIREBASE_CLIENT_ID`

## 🔑 環境變數設置

編輯 `.env` 檔案並添加以下配置：

```env
# 啟用 Firestore
USE_FIRESTORE=true

# Firebase 配置 (從服務帳號金鑰取得)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789
```

### ⚠️ 環境變數注意事項

**處理 FIREBASE_PRIVATE_KEY 中的換行符：**

1. 從 JSON 檔案複製 `private_key` 值
2. 它會是這種格式：
   ```
   "-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n"
   ```
3. 直接複製到 `.env` 檔案（包括 `\n` 字符）
4. 或者，如果使用 shell 環境，可以轉換為實際的換行：
   ```bash
   export FIREBASE_PRIVATE_KEY=$(cat /path/to/private_key.txt)
   ```

## 📦 部署 Firestore 安全規則

```bash
# 檢視當前規則
firebase firestore:get rules

# 部署新規則
firebase deploy --only firestore:rules

# 部署完整配置
firebase deploy
```

## 📊 Firestore 資料結構

### Collections 說明

#### 1. `members` - 會員資料
```json
{
  "userId": "user123",          // 文件 ID
  "name": "李明",
  "phone": "0912345678",
  "address": "台北市中山區",
  "birthDate": "1990-01-01",
  "address2": "補充地址",
  "createdAt": "2024-01-17T10:30:00+08:00",
  "updatedAt": "2024-01-17T10:30:00+08:00"
}
```

#### 2. `orders` - 訂單資料
```json
{
  "orderId": "ORD12345678",      // 文件 ID
  "userId": "user123",
  "items": "土雞蛋 x11 (急需)",
  "amount": 2500,
  "status": "已完成",
  "paymentStatus": "已付款",
  "paymentMethod": "ecpay",
  "deliveryLogs": [
    {
      "date": "2024-01-15T14:30:00+08:00",
      "qty": 5,
      "address": "台北市中山區"
    }
  ],
  "createdAt": "2024-01-15T10:30:00+08:00",
  "updatedAt": "2024-01-15T14:30:00+08:00"
}
```

#### 3. `auditLogs` - 審計日誌 (出貨修正記錄)
```json
{
  "timestamp": "2024-01-17T15:45:00+08:00",
  "orderId": "ORD12345678",
  "operation": "update_delivery",
  "adminName": "管理員名稱",
  "beforeValue": "qty:5 addr:台北市中山區",
  "afterValue": "qty:7 addr:台北市內湖區",
  "reason": "客戶要求修正地址"
}
```

## 🔄 資料遷移

### 從 Google Sheets 遷移至 Firestore

建議使用分階段遷移：

#### 步驟 1: 平行運行 (測試階段)
```env
USE_FIRESTORE=false  # 保持使用 Google Sheets
```
- 所有新資料先寫入 Google Sheets
- 驗證 Firestore 連接和規則

#### 步驟 2: 匯入歷史資料
```python
# 使用提供的 migration_script.py (需自行建立)
# 從 Google Sheets 讀取所有資料，寫入 Firestore
python migration_script.py
```

#### 步驟 3: 切換至 Firestore
```env
USE_FIRESTORE=true  # 改用 Firestore
```
- 所有新資料寫入 Firestore
- 保留 Google Sheets 作為備份

#### 步驟 4: 驗證並清理
- 比對兩邊資料
- 確認沒有遺漏
- 可選：停用 Google Sheets 服務

## 🧪 測試連接

```bash
# 安裝依賴
pip install -r requirements.txt

# 測試 Firestore 連接
python -c "
from services.firestore_service import FirestoreService
FirestoreService.init()
print('✅ Firebase Firestore 連接成功！')
"
```

## 📈 效能提升

### 預期效能改善

| 操作 | Google Sheets | Firestore |
|-----|--------------|-----------|
| 新增記錄 | 2-5 秒 | 100-500 ms |
| 查詢單筆 | 1-3 秒 | 10-50 ms |
| 查詢全部 | 5-15 秒 | 100-300 ms |
| 更新記錄 | 2-5 秒 | 50-200 ms |

### 優勢
✅ 更快的讀寫速度  
✅ 實時資料同步  
✅ 自動備份和版本控制  
✅ 內建安全規則  
✅ 擴展性更好  

## 🔒 安全最佳實踐

1. **不要提交敏感金鑰到 Git**
   ```bash
   echo ".env" >> .gitignore
   git rm --cached .env
   ```

2. **定期輪換服務帳號**
   - 每年至少輪換一次金鑰

3. **使用強密碼保護 Firebase 專案**
   - 啟用 2FA 認證

4. **監視 Firestore 使用情況**
   - Firebase Console → Quotas 頁籤

## 🆘 常見問題

### 連接超時
- 檢查 `FIREBASE_PRIVATE_KEY` 格式（\n 不能被轉換）
- 確保網路連接正常
- 檢查防火牆設定

### 權限被拒
- 驗證服務帳號金鑰正確
- 檢查 Firestore 安全規則
- 確認服務帳號具有適當權限

### 資料未同步
- 檢查 `USE_FIRESTORE` 設置
- 查看應用程式日誌
- 確認 Firestore 資料庫狀態

## 📞 支援資源

- [Firebase 官方文件](https://firebase.google.com/docs)
- [Firestore 最佳實踐](https://firebase.google.com/docs/firestore/best-practices)
- [Firebase Admin SDK (Python)](https://firebase.google.com/docs/database/admin/start)

---

**最後更新**: 2024-01-17  
**適用於**: Firebase Firestore 最新版本
