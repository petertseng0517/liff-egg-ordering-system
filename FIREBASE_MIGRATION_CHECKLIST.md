# Firebase Firestore 遷移檢查清單

## ✅ 程式修改清單

### 已完成的修改

- [x] **requirements.txt** - 新增 `firebase-admin==6.2.0` 依賴
- [x] **config.py** - 添加 Firebase 配置參數
- [x] **services/firestore_service.py** - 創建 Firestore 服務層
- [x] **services/database_adapter.py** - 創建資料庫適配器 (支持雙資料庫)
- [x] **routes/admin.py** - 更新為使用 DatabaseAdapter
- [x] **routes/member.py** - 更新為使用 DatabaseAdapter
- [x] **routes/ecpay.py** - 更新為使用 DatabaseAdapter
- [x] **app.py** - 添加 Firestore 初始化邏輯
- [x] **.env.example** - 提供環境變數模板
- [x] **firestore.rules** - Firebase 安全規則
- [x] **firebase.json** - Firebase CLI 配置
- [x] **FIREBASE_SETUP.md** - 完整設置指南
- [x] **migration_script.py** - 資料遷移腳本

## 🔧 部署步驟

### 第一步：安裝依賴

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝 Firebase CLI (一次性)
npm install -g firebase-tools
# 或
brew install firebase-cli
```

### 第二步：設置 Firebase 專案

```bash
# 登入 Firebase
firebase login

# 初始化 Firebase 專案
firebase init firestore
# 選擇選項:
# - Firestore 位置: asia-northeast1 (日本)
# - 使用規則預設值: 稍後手動更新
```

### 第三步：配置環境變數

1. 從 Firebase Console 下載服務帳號金鑰
2. 編輯 `.env` 檔案，添加：
   ```env
   USE_FIRESTORE=false  # 先測試 Google Sheets
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
   FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your-client-id
   ```

### 第四步：測試連接

```bash
# 測試 Firestore 連接
python -c "
from config import Config
if Config.USE_FIRESTORE:
    from services.firestore_service import FirestoreService
    FirestoreService.init()
    print('✅ Firestore 連接成功')
else:
    print('ℹ️  當前使用 Google Sheets')
"
```

### 第五步：部署 Firestore 規則

```bash
# 檢視當前規則
firebase firestore:get rules

# 部署新規則
firebase deploy --only firestore:rules
```

### 第六步：資料遷移 (可選)

```bash
# 執行遷移腳本
python migration_script.py

# 驗證遷移結果
# 腳本會自動驗證，或手動檢查 Firebase Console
```

### 第七步：切換至 Firestore

編輯 `.env` 設置：
```env
USE_FIRESTORE=true
```

重新啟動應用：
```bash
python app.py
```

## 🧪 測試檢查

- [ ] 新增會員 - 驗證資料寫入 Firestore
- [ ] 建立訂單 - 驗證訂單和金額正確
- [ ] 更新訂單狀態 - 驗證 Firestore 有更新
- [ ] 新增出貨紀錄 - 驗證出貨日誌
- [ ] LINE 通知 - 驗證推送消息正常
- [ ] ECPay 回調 - 驗證付款狀態更新

## 📊 效能監視

### Firestore 使用情況

1. 登入 [Firebase Console](https://console.firebase.google.com/)
2. 進入您的專案
3. 查看 **Firestore Database** 頁籤
4. 監視：
   - **Read ops** - 讀取操作數
   - **Write ops** - 寫入操作數
   - **Delete ops** - 刪除操作數
   - **儲存空間** - 資料大小

### 成本估算

Firestore 採用按用量計費：
- **讀取**: 每 100,000 次 $0.06
- **寫入**: 每 100,000 次 $0.18
- **刪除**: 每 100,000 次 $0.02
- **存儲**: 每 GB 每月 $0.18

預估月成本 (小規模應用):
- 1,000 訂單/月 × 5 次操作 = $0.09

## ⚠️ 常見問題排查

### 問題：`Authentication Failed`
**原因**: 服務帳號金鑰不正確或過期
**解決**:
1. 重新下載服務帳號金鑰
2. 檢查環境變數格式
3. 確保 `\n` 字符正確保留

### 問題：`Permission Denied`
**原因**: Firestore 安全規則限制
**解決**:
```bash
firebase firestore:get rules  # 檢查規則
firebase deploy --only firestore:rules  # 重新部署
```

### 問題：資料未出現在 Firestore
**原因**: `USE_FIRESTORE` 仍未啟用
**解決**:
```bash
echo "USE_FIRESTORE=true" >> .env
# 或編輯 .env 檔案直接修改
```

### 問題：遷移腳本失敗
**原因**: Google Sheets 和 Firestore 連接問題
**解決**:
1. 驗證 Google Sheets 服務帳號正確
2. 驗證 Firebase 服務帳號正確
3. 檢查工作表名稱是否正確

## 📝 回滾計劃

如果需要回滾到 Google Sheets：

```bash
# 1. 編輯 .env
USE_FIRESTORE=false

# 2. 重新啟動應用
python app.py

# 3. 驗證
# 檢查日誌看是否切換回 Google Sheets
```

## 🔐 安全建議

1. **不要提交 .env 到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **定期輪換金鑰**
   - 每 90 天更新一次服務帳號金鑰

3. **限制 Firebase 權限**
   - 只授予必要的資料庫權限
   - 定期審計存取日誌

4. **啟用 Firestore 備份**
   - Firebase 自動每日備份
   - 可配置長期保留

## 📞 支援資源

- **Firebase 文件**: https://firebase.google.com/docs
- **Firestore 指南**: https://firebase.google.com/docs/firestore
- **Python Admin SDK**: https://firebase.google.com/docs/database/admin/start
- **Discord 社群**: Firebase 官方社群

---

**遷移日期**: 2024-01-17  
**版本**: 1.0  
**最後更新**: 2024-01-17
