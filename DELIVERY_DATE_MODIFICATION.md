# 出貨紀錄欄位修改說明

## 修改時間
2026-01-18 12:05 (Asia/Taipei)

## 修改內容

### 1. 資料結構變更

#### 前：deliveryLogs 結構
```json
{
  "date": "2026-01-18 11:52",
  "qty": 10,
  "address": "新竹市..."
}
```

#### 後：deliveryLogs 結構
```json
{
  "stamp": "2026-01-18 11:52:00",  // 系統記錄時間戳記
  "delivery_date": "2026-01-18",    // 與客戶約定的出貨日期
  "qty": 10,
  "address": "新竹市...",
  "date": "2026-01-18 11:52"        // 保留兼容性
}
```

### 2. 表格欄位變更

#### 前：出貨紀錄表格
| 出貨日期 | 數量 | 出貨地點 | 狀態 | 操作 |
|---------|------|--------|------|------|

#### 後：出貨紀錄表格
| Stamp | 出貨日期 | 數量 | 出貨地點 | 狀態 | 操作 |
|-------|---------|------|--------|------|------|

**說明：**
- **Stamp**：系統自動記錄紀錄產生的時間（時間戳記），不可編輯
- **出貨日期**：管理者可自行填寫與客戶約定的出貨日期

### 3. 新增出貨表單

#### 新增欄位
```html
<input type="date" id="new-delivery-date" placeholder="出貨日期">
```

**說明：**
- 管理者在新增出貨紀錄時，可選擇性填寫出貨日期
- 若未填寫，系統將使用當天日期作為預設值

### 4. 後端修改

#### firestore_service.py

**add_delivery_log() 函數**
```python
@classmethod
def add_delivery_log(cls, order_id, qty, address="", delivery_date=""):
    """新增出貨紀錄"""
    # ...
    new_log = {
        "stamp": now.strftime('%Y-%m-%d %H:%M:%S'),  # 系統時間戳
        "delivery_date": delivery_date or now.strftime('%Y-%m-%d'),  # 客戶日期
        "qty": qty,
        "address": address
    }
```

**correct_delivery_log() 函數**
- 修正紀錄時，保留原有的 `stamp` 和 `delivery_date` 欄位
- 確保修正歷史完整性

#### routes/admin.py

**add_delivery_log() 路由**
- 新增接收 `delivery_date` 參數
- 將參數傳遞給 `DatabaseAdapter.add_delivery_log()`

### 5. 前端修改

#### templates/admin.html

**新增出貨表單**
- 添加日期輸入欄位 `#new-delivery-date`

**renderDeliveryLogs() 函數**
- 顯示 `stamp` 欄位（系統時間戳）
- 顯示 `delivery_date` 欄位（客戶日期）
- 兼容舊資料：`log.stamp || log.date`

**addDeliveryLog() 函數**
- 收集日期輸入值
- 傳送 `delivery_date` 參數到 API
- 清空日期輸入欄位

### 6. 向後相容性

✅ **自動處理舊資料**
- 使用 `log.stamp || log.date` 兼容舊記錄
- 修正時自動補充新欄位
- 前端顯示 `(未指定)` 作為未設定出貨日期的預設值

## 應用重啟
```bash
pkill -f "python.*app.py"
bash start_app.sh
```

## 測試清單

- [ ] 載入舊訂單，檢查是否正確顯示
- [ ] 新增出貨紀錄，填寫出貨日期
- [ ] 修正出貨紀錄，檢查日期保留
- [ ] 驗證修正歷史正確性
- [ ] 測試未填寫出貨日期的情況

## 修改影響範圍

| 檔案 | 修改內容 |
|------|--------|
| services/firestore_service.py | 新增 stamp 和 delivery_date 欄位 |
| routes/admin.py | 接收 delivery_date 參數 |
| templates/admin.html | 新增表單欄位，更新表格結構 |

## 符號定義

- **Stamp**：記錄產生時間（系統自動，不可編輯）
- **出貨日期**：與客戶約定的日期（管理者手動輸入）
