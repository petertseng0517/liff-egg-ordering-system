# 📖 快速部署指南

## 🚀 本地開發

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 環境設置

創建 `.env` 文件：

```env
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-change-in-production
ADMIN_PASSWORD=your-admin-password

# Google Sheets
SPREADSHEET_ID=your-spreadsheet-id

# LINE Bot
LINE_CHANNEL_ACCESS_TOKEN=your-line-token

# ECPay (預設為測試環境)
ECPAY_MERCHANT_ID=2000132
ECPAY_HASH_KEY=5294y06JbISpM5x9
ECPAY_HASH_IV=v77hoKGq4kWxNNIS
```

### 3. 運行應用

```bash
python app.py
```

訪問：http://localhost:5000

### 4. 運行測試

```bash
# 執行所有測試
python -m unittest discover tests -v

# 或使用 pytest
pytest tests/ -v --tb=short

# 生成覆蓋率報告
pytest tests/ --cov --cov-report=html
```

---

## 🌐 部署到 Render.com

### 1. 創建 Render 應用

1. 進入 [Render.com](https://render.com)
2. 點擊「New」→「Web Service」
3. 連接你的 GitHub 倉庫

### 2. 配置環境變數

在 Render 專案設定中添加：

```
APP_BASE_URL=https://your-app.onrender.com
FLASK_SECRET_KEY=your-production-secret-key
ADMIN_PASSWORD=your-admin-password
SPREADSHEET_ID=your-spreadsheet-id
LINE_CHANNEL_ACCESS_TOKEN=your-line-token
ECPAY_MERCHANT_ID=2000132
ECPAY_HASH_KEY=5294y06JbISpM5x9
ECPAY_HASH_IV=v77hoKGq4kWxNNIS
```

### 3. 部署

Procfile 已配置，推送到 GitHub 後自動部署：

```bash
git push origin main
```

### 4. 驗證部署

訪問：https://your-app.onrender.com

---

## 🔐 安全性檢查清單

部署前確保：

- [ ] 生成強密碼並設置 `ADMIN_PASSWORD`
- [ ] 生成隨機密鑰並設置 `FLASK_SECRET_KEY`
- [ ] 設置 `APP_BASE_URL` 為正式域名
- [ ] LINE 和 ECPay 憑證已驗證
- [ ] Google Sheets service account 已正確配置
- [ ] 啟用 HTTPS（Render 自動支援）
- [ ] 測試登入速率限制功能
- [ ] 檢查日誌文件權限

---

## 📝 常見問題

### Q: 為什麼登入被鎖定？
A: 密碼錯誤 5 次後會鎖定 5 分鐘。等待後重試，或查看日誌確認。

### Q: 表單驗證提示說"電話格式不正確"？
A: 請輸入 10 位數字，例如：0912345678

### Q: LINE LIFF 無法初始化？
A: 確認 LIFF ID 正確，並在 LINE Developers 設置中添加應用 URL。

### Q: ECPay 付款無法完成？
A: 確保使用測試環境憑證並已配置 `APP_BASE_URL`。

---

## 🛠️ 故障排除

### 檢查日誌

```bash
# 查看 Flask 應用日誌
tail -f ecpay_callback.log

# Render 日誌
# 在 Render 專案頁面查看「Logs」
```

### 重新安裝依賴

```bash
pip install --upgrade -r requirements.txt
```

### 清除 Python 快取

```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete
```

---

## 📞 支援

遇到問題？查看：
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 詳細改進文檔
- [README.md](README.md) - 原始功能說明
- Flask 文檔：https://flask.palletsprojects.com/
- LINE LIFF：https://developers.line.biz/en/docs/liff/

---

**最後更新：2026-01-06**
