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
    
    # 組合商品字串，例如: "放山土雞蛋(10入) x2 (備註: 放門口)"
    item_str = f"{item_name} x{qty}"
    if remarks:
        item_str += f" ({remarks})"

    # 寫入: 訂單編號, UserId, 商品, 金額, 日期, 狀態
    sheet.append_row([
        order_id,
        user_id,
        item_str,
        total_amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "處理中"
    ])
    return jsonify({"status": "success", "msg": "訂購成功", "orderId": order_id})

@app.route('/api/history', methods=['POST'])
def history():
    data = request.json
    user_id = data.get('userId')
    sheet = get_sheet("Orders")
    all_records = sheet.get_all_values() # 抓取所有資料
    
    # 標題列是第0列，資料從第1列開始
    # 欄位索引: A=0(ID), B=1(UserId), C=2(Item), D=3(Amt), E=4(Date), F=5(Status)
    history_list = []
    
    for row in all_records[1:]: # 跳過標題
        if len(row) > 1 and row[1] == user_id:
            history_list.append({
                "orderId": row[0],
                "items": row[2],
                "amount": row[3],
                "date": row[4],
                "status": row[5]
            })
            
    return jsonify(history_list)

# === Admin API ===

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
        # Order Cols: ID=0, UserId=1, Items=2, Amt=3, Date=4, Status=5
        uid = row[1]
        customer = member_map.get(uid, {})
        
        results.append({
            "orderId": row[0],
            "userId": uid,
            "items": row[2],
            "amount": row[3],
            "date": row[4],
            "status": row[5],
            "customer": customer
        })
    
    return jsonify(results)

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