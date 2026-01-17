# 本地測試指南

## ✅ 測試環境準備

### 1. Python 依賴檢查
```bash
pip install -r requirements.txt
```

### 2. 環境變數設置

**選項 A：繼續使用 Google Sheets (推薦先測試)**
```bash
# 編輯 .env
USE_FIRESTORE=false
SPREADSHEET_ID=your-existing-spreadsheet-id
# 保留其他設置
```

**選項 B：測試 Firebase Firestore**
需先完成 Firebase 設置，參考 [FIREBASE_SETUP.md](./FIREBASE_SETUP.md)

## 🧪 測試步驟

### 1. 啟動應用
```bash
python app.py
# 應該看到類似輸出：
# * Running on http://127.0.0.1:5005
```

### 2. 測試 Google Sheets (現有功能)

#### 測試 - 新增會員
```bash
curl -X POST http://localhost:5005/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user_001",
    "name": "測試用戶",
    "phone": "0912345678",
    "address": "台北市中山區",
    "birthDate": "1990-01-01",
    "address2": ""
  }'

# 預期回應: {"status": "success"}
```

#### 測試 - 檢查會員
```bash
curl -X POST http://localhost:5005/api/check_member \
  -H "Content-Type: application/json" \
  -d '{"userId": "test_user_001"}'

# 預期回應: {"registered": true, "name": "測試用戶", ...}
```

#### 測試 - 建立訂單
```bash
curl -X POST http://localhost:5005/api/order \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user_001",
    "itemName": "土雞蛋1盤",
    "qty": 5,
    "remarks": "測試訂單",
    "paymentMethod": "transfer"
  }'

# 預期回應: {"status": "success", "orderId": "ORDxxxxxxxxxx"}
```

#### 測試 - 查詢訂單歷史
```bash
curl -X POST http://localhost:5005/api/history \
  -H "Content-Type: application/json" \
  -d '{"userId": "test_user_001"}'

# 預期回應: [{"orderId": "...", "items": "...", ...}]
```

### 3. 驗證資料庫適配器

#### 檢查日誌輸出
查看應用日誌，確認使用的是 Google Sheets：
```bash
tail -f ecpay_callback.log | grep -i "sheets\|firestore"

# 應該看到:
# Google Sheets initialized successfully
```

### 4. 切換至 Firestore 測試 (可選)

*準備好 Firebase 後才進行此步驟*

```bash
# 編輯 .env
USE_FIRESTORE=true

# 重新啟動應用
python app.py

# 檢查日誌
tail -f ecpay_callback.log | grep -i "firestore"

# 應該看到:
# Firebase Firestore initialized successfully
```

## 📝 測試檢查表

### 基礎功能測試 (Google Sheets)
- [ ] 應用正常啟動，無錯誤
- [ ] 新增會員成功
- [ ] 檢查會員存在
- [ ] 編輯會員資料成功
- [ ] 建立訂單成功
- [ ] 查詢訂單歷史成功
- [ ] 日誌顯示 "Google Sheets initialized"

### Firestore 功能測試 (可選)
- [ ] Firebase 連接成功
- [ ] 新增會員至 Firestore
- [ ] 從 Firestore 查詢會員
- [ ] 建立訂單至 Firestore
- [ ] 查詢 Firestore 訂單
- [ ] 日誌顯示 "Firebase Firestore initialized"

### 管理員功能測試 (需登入)
- [ ] 登入管理員後台
- [ ] 查看所有訂單 `/api/admin/orders`
- [ ] 更新訂單狀態
- [ ] 新增出貨紀錄
- [ ] 查看審計日誌

### 資料庫切換測試
- [ ] 將 `USE_FIRESTORE` 從 false 改為 true
- [ ] 重新啟動應用
- [ ] 驗證新資料寫入 Firestore
- [ ] 將 `USE_FIRESTORE` 改回 false
- [ ] 應用能正常回滾至 Google Sheets

## 🐛 故障排除

### 問題：應用啟動失敗
**症狀**: `ImportError: No module named 'services.database_adapter'`

**解決**:
```bash
# 確保新文件已建立
ls -la services/database_adapter.py
ls -la services/firestore_service.py

# 重新安裝依賴
pip install -r requirements.txt
```

### 問題：Google Sheets 連接失敗
**症狀**: `Error in get_all_orders: ...`

**解決**:
```bash
# 檢查 service_account.json 存在
ls -la service_account.json

# 檢查 SPREADSHEET_ID 正確
echo $SPREADSHEET_ID
```

### 問題：Firebase 連接失敗
**症狀**: `Failed to initialize Firebase: ...`

**解決**:
```bash
# 驗證環境變數
echo $FIREBASE_PROJECT_ID
echo $FIREBASE_CLIENT_EMAIL

# 檢查 private_key 格式
echo $FIREBASE_PRIVATE_KEY | head -c 50
# 應該看到: -----BEGIN PRIVATE KEY-----\nMII...
```

## 📊 效能測試

### 測試查詢速度 (Google Sheets vs Firestore)

```bash
# 時間測試工具
time python -c "
from services.database_adapter import DatabaseAdapter
orders = DatabaseAdapter.get_all_orders_with_members()
print(f'取得 {len(orders)} 筆訂單')
"

# 記錄執行時間，比對差異
```

## ✨ 測試完成檢查

完成所有測試後：

- [ ] 所有 API 端點能正常運作
- [ ] 資料正確寫入資料庫
- [ ] 可以在兩個數據庫間切換
- [ ] 沒有遺漏或報錯
- [ ] 效能符合預期

---

**下一步**: 
- 所有測試通過後，可以考慮遷移至生產環境
- 或進行資料遷移 (使用 migration_script.py)
- 或提交 git 並部署到伺服器
