from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)

# === 設定 Google Sheets 連線 ===
# 請確保 service_account.json 檔案在同一個資料夾下
SCOPE = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDS = Credentials.from_service_account_file('service_account.json', scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)

# 您的試算表 ID (從網址複製的那一長串)
SPREADSHEET_ID = '1PybjjWlzhBw402wUC3gbTVclvYAgVqDTVIPT5ovXDIU' 

def get_sheet(sheet_name):
    try:
        sheet = CLIENT.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        return sheet
    except Exception as e:
        print(f"連線錯誤: {e}")
        return None

# === 路由 (Routes) ===

@app.route('/')
def home():
    # 這行會自動去 templates 資料夾找 index.html
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    sheet = get_sheet("Members")
    # 寫入: UserId, Name, Phone, Address
    sheet.append_row([data.get('userId'), data.get('name'), data.get('phone'), data.get('address')])
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

if __name__ == '__main__':
    # debug=True 代表您改程式碼存檔，網頁會自動更新
    app.run(debug=True, port=5000)