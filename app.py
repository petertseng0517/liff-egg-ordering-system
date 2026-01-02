from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LINE Bot SDK v3
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

# === 設定 Google Sheets 連線 ===
# 請確保 service_account.json 檔案在同一個資料夾下
SCOPE = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDS = Credentials.from_service_account_file('service_account.json', scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)

# 您的試算表 ID (從網址複製的那一長串)
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# === LINE Bot 設定 ===
# 請填入您的 LINE Channel Access Token
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

def get_sheet(sheet_name):
    try:
        sheet = CLIENT.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        return sheet
    except Exception as e:
        print(f"連線錯誤: {e}")
        return None

def send_line_push(user_id, text):
    if not LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_ACCESS_TOKEN == 'YOUR_CHANNEL_ACCESS_TOKEN':
        print("未設定 LINE Token，跳過推播")
        return
    
    try:
        configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            push_message_request = PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=text)]
            )
            line_bot_api.push_message(push_message_request)
            print(f"推播成功: {user_id}")
    except Exception as e:
        print(f"推播失敗: {e}")

# === 路由 (Routes) ===

@app.route('/')
def home():
    # 這行會自動去 templates 資料夾找 index.html
    return render_template('index.html')

# --- Login System ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error="密碼錯誤")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/admin')
def admin_page():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('admin.html')
# --------------------

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    sheet = get_sheet("Members")
    # 寫入: UserId, Name, Phone, Address, BirthDate, Address2
    sheet.append_row([
        data.get('userId'), 
        data.get('name'), 
        data.get('phone'), 
        data.get('address'),
        data.get('birthDate'),
        data.get('address2')
    ])
    return jsonify({"status": "success", "msg": "註冊成功"})

@app.route('/api/check_member', methods=['POST'])
def check_member():
    data = request.json
    user_id = data.get('userId')
    sheet = get_sheet("Members")
    
    # 取得所有會員資料 (包含標題)
    all_members = sheet.get_all_values()
    
    # 假設 UserId 在第一欄 (index 0), Name 在第二欄 (index 1)
    # 從第二行開始找 (跳過標題)
    for row in all_members[1:]:
        if len(row) > 0 and row[0] == user_id:
            return jsonify({"registered": True, "name": row[1]})
            
    return jsonify({"registered": False})

# 產品清單與價格 (Backend Source of Truth)
PRODUCTS = {
    "土雞蛋11盤": 2500,
    "土雞蛋1盤": 250
}

@app.route('/api/order', methods=['POST'])
def order():
    data = request.json
    sheet = get_sheet("Orders")
    
    user_id = data.get('userId')
    item_name = data.get('itemName')
    try:
        qty = int(data.get('qty', 1))
    except:
        qty = 1
    remarks = data.get('remarks', '')

    # 1. 驗證商品與價格
    unit_price = PRODUCTS.get(item_name)
    if not unit_price:
        return jsonify({"status": "error", "msg": "商品不存在"}), 400
    
    total_amount = unit_price * qty
    
    # 2. 產生訂單資料
    order_id = "ORD" + str(int(datetime.now().timestamp()))
    
    # 針對商品名稱進行正規化，確保 item_str 中的數量是實際盤數
    actual_item_name = item_name # 實際寫入 Google Sheet 的商品名稱，可能修改
    actual_qty = qty             # 實際盤數

    if item_name == "土雞蛋11盤":
        actual_qty = qty * 11
        # 可以選擇保留原始資訊，例如改成 "土雞蛋(11盤優惠組)"
        actual_item_name = "土雞蛋(11盤優惠組)"
    elif item_name == "土雞蛋1盤": # 確保這裡只處理了單盤的情況，其他商品名稱則按原樣處理
        actual_qty = qty * 1
        actual_item_name = "土雞蛋"

    # 組合商品字串，例如: "土雞蛋 x22 (備註: 放門口)"
    item_str_for_sheet = f"{actual_item_name} x{actual_qty}"
    if remarks:
        item_str_for_sheet += f" ({remarks})"

    sheet.append_row([
        order_id,
        user_id,
        item_str_for_sheet, # 使用正規化後的字串
        total_amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "處理中",
        "",         # DeliveryLogs
        "未付款"     # PaymentStatus
    ])

    # === 發送 LINE 訂單確認訊息給客戶 ===
    order_confirm_msg = (
        f"✅ 訂單已送出\n"
        f"訂單編號: {order_id}\n"
        f"商品: {item_str_for_sheet}\n"
        f"總金額: ${total_amount}\n"
        f"付款狀態: 未付款\n"
        f"\n我們將盡快處理您的訂單！"
    )
    send_line_push(user_id, order_confirm_msg)
    # ==================================

    return jsonify({"status": "success", "msg": "訂購成功", "orderId": order_id})

@app.route('/api/history', methods=['POST'])
def history():
    data = request.json
    user_id = data.get('userId')
    sheet = get_sheet("Orders")
    all_records = sheet.get_all_values() # 抓取所有資料
    
    # 標題列是第0列，資料從第1列開始
    # 欄位索引: A=0(ID), B=1(UserId), C=2(Item), D=3(Amt), E=4(Date), F=5(Status), G=6(Logs), H=7(Payment)
    history_list = []
    
    for row in all_records[1:]: # 跳過標題
        if len(row) > 1 and row[1] == user_id:
            # 兼容舊資料 (可能沒有 H 欄)
            pay_status = row[7] if len(row) > 7 else "未付款"

            history_list.append({
                "orderId": row[0],
                "items": row[2],
                "amount": row[3],
                "date": row[4],
                "status": row[5],
                "paymentStatus": pay_status
            })
            
    return jsonify(history_list)

# === Admin API ===

import json
@app.route('/api/admin/orders', methods=['GET'])
def admin_orders():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    # 1. Get Members for mapping
    member_sheet = get_sheet("Members")
    members_data = member_sheet.get_all_values()
    member_map = {}
    # Skip header
    for row in members_data[1:]:
        if len(row) > 0:
            # UserId is row[0]
            m_info = {
                "name": row[1] if len(row) > 1 else "",
                "phone": row[2] if len(row) > 2 else "",
                "address": row[3] if len(row) > 3 else "",
                "birthDate": row[4] if len(row) > 4 else "",
                "address2": row[5] if len(row) > 5 else ""
            }
            member_map[row[0]] = m_info

    # 2. Get Orders
    order_sheet = get_sheet("Orders")
    orders_data = order_sheet.get_all_values()
    
    results = []
    # Skip header
    for row in orders_data[1:]:
        if len(row) < 6: continue
        # Order Cols: ID=0, UserId=1, Items=2, Amt=3, Date=4, Status=5, Logs=6, Payment=7
        uid = row[1]
        customer = member_map.get(uid, {})
        
        # Parse Delivery Logs (Column G)
        logs = []
        if len(row) > 6 and row[6]:
            try:
                logs = json.loads(row[6])
            except:
                logs = []

        # Parse Payment Status (Column H)
        pay_status = row[7] if len(row) > 7 else "未付款"

        results.append({
            "orderId": row[0],
            "userId": uid,
            "items": row[2],
            "amount": row[3],
            "date": row[4],
            "status": row[5],
            "deliveryLogs": logs,
            "paymentStatus": pay_status,
            "customer": customer
        })
    
    return jsonify(results)

@app.route('/api/admin/order/add_delivery', methods=['POST'])
def admin_add_delivery():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    order_id = data.get('orderId')
    user_id = data.get('userId')
    qty = int(data.get('qty', 0))
    total_ordered = int(data.get('totalOrdered', 1))

    sheet = get_sheet("Orders")
    try:
        cell = sheet.find(order_id)
        if not cell:
            return jsonify({"status": "error", "msg": "找不到訂單"}), 404
        
        # Get current logs (Column G = 7)
        row_values = sheet.row_values(cell.row)
        current_logs_str = row_values[6] if len(row_values) > 6 else "[]"
        try:
            logs = json.loads(current_logs_str)
            if not isinstance(logs, list): logs = []
        except:
            logs = []
            
        # Add new log
        new_log = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "qty": qty
        }
        logs.append(new_log)
        
        # Calculate new status
        total_delivered = sum(int(l['qty']) for l in logs)
        new_status = "已完成" if total_delivered >= total_ordered else "部分配送"
        
        # Update Sheet
        # Status -> Col 6, Logs -> Col 7
        sheet.update_cell(cell.row, 6, new_status) 
        sheet.update_cell(cell.row, 7, json.dumps(logs, ensure_ascii=False))
        
        # Push Notification
        msg = f"📦 出貨通知\n您好，我們已為您出貨 {qty} 盤土雞蛋。\n目前進度: {total_delivered}/{total_ordered} 盤。"
        if new_status == "已完成":
            msg += "\n🎉 您的訂單已全數出貨完畢，感謝您的訂購！"
        else:
            msg += "\n其餘商品將盡快安排配送。"
            
        send_line_push(user_id, msg)
        
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error adding delivery: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/order/update_payment', methods=['POST'])
def admin_update_payment():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    order_id = data.get('orderId')
    new_payment = data.get('paymentStatus')
    
    if not order_id or not new_payment:
        return jsonify({"status": "error", "msg": "缺少參數"}), 400

    sheet = get_sheet("Orders")
    try:
        cell = sheet.find(order_id)
        if not cell:
            return jsonify({"status": "error", "msg": "找不到訂單"}), 404
        
        # Update Payment Status column (Column H = 8)
        sheet.update_cell(cell.row, 8, new_payment)
        
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error updating payment: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/admin/order/update_status', methods=['POST'])
def admin_update_status():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    order_id = data.get('orderId')
    new_status = data.get('status')
    user_id = data.get('userId') # For push notification
    
    if not order_id or not new_status:
        return jsonify({"status": "error", "msg": "缺少參數"}), 400

    sheet = get_sheet("Orders")
    try:
        # Find the row (gspread find)
        cell = sheet.find(order_id)
        if not cell:
            return jsonify({"status": "error", "msg": "找不到訂單"}), 404
        
        # Update Status column (Column F = 6)
        sheet.update_cell(cell.row, 6, new_status)
        
        # Push Notification
        if user_id:
            msg_map = {
                "已確認": "您的訂單已確認，我們將盡快安排。",
                "配送中": "您的蛋已經出發囉！請留意電話。",
                "已完成": "訂單已完成，感謝您的購買！",
                "已取消": "您的訂單已取消。"
            }
            msg = msg_map.get(new_status, f"您的訂單狀態已更新為：{new_status}")
            send_line_push(user_id, msg)
            
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
    # debug=True 代表您改程式碼存檔，網頁會自動更新
    app.run(debug=True, port=5000)