#!/bin/bash
# 啟動腳本 - 確保使用虛擬環境

# 停止現有的應用進程
echo "停止現有進程..."
pkill -f "app.py" || true
sleep 1

# 變更到應用目錄
cd /Users/peter/ai_eggs

# 啟動應用
echo "啟動應用..."
/Users/peter/ai_eggs/.venv/bin/python app.py

