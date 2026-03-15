"""
遷移腳本：為舊訂單添加 actualQuantity 和 orderQty 字段

使用方法：
  python migrate_orders.py

此腳本會：
1. 遍歷所有訂單
2. 對於沒有 actualQuantity 的訂單，嘗試找到對應的商品
3. 添加 actualQuantity 和 orderQty 字段
"""

import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Firebase
if not firebase_admin._apps:
    creds_dict = {
        "type": "service_account",
        "project_id": Config.FIREBASE_PROJECT_ID,
        "private_key": Config.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if Config.FIREBASE_PRIVATE_KEY else None,
        "client_email": Config.FIREBASE_CLIENT_EMAIL,
        "client_id": Config.FIREBASE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def migrate_orders():
    """遷移所有舊訂單"""
    orders_ref = db.collection('orders')
    orders = orders_ref.stream()
    
    total_orders = 0
    updated_orders = 0
    skipped_orders = 0
    
    for order_doc in orders:
        total_orders += 1
        order = order_doc.to_dict()
        order_id = order.get('orderId', '')
        
        # 檢查是否已經有 actualQuantity 字段
        if 'actualQuantity' in order and 'orderQty' in order:
            logger.info(f"[SKIP] {order_id} - 已有 actualQuantity 和 orderQty")
            skipped_orders += 1
            continue
        
        # 從 items 字符串中提取訂購數量
        items_str = order.get('items', '')
        match = re.search(r'x(\d+)', items_str)
        order_qty = int(match.group(1)) if match else 1
        
        # 嘗試從商品名稱找到實際數量
        actual_quantity = 1  # 默認值
        
        # 從 items 中提取商品名稱（去掉 x 及其後面的內容和備註）
        product_name = items_str.split(' x')[0].split(' (')[0].strip()
        
        if product_name:
            # 搜索具有相同名稱的商品
            products = db.collection('products').where('name', '==', product_name).stream()
            for product_doc in products:
                product = product_doc.to_dict()
                actual_quantity = product.get('actualQuantity', 1)
                logger.info(f"[FOUND] {order_id} - 找到商品：{product_name}，實際數量：{actual_quantity}")
                break
        
        # 更新訂單
        try:
            orders_ref.document(order_id).update({
                'actualQuantity': int(actual_quantity),
                'orderQty': int(order_qty)
            })
            updated_orders += 1
            logger.info(f"[UPDATE] {order_id} - orderQty={order_qty}, actualQuantity={actual_quantity}, expected_total={order_qty * actual_quantity}")
        except Exception as e:
            logger.error(f"[ERROR] {order_id} - 更新失敗：{e}")
    
    logger.info(f"\n" + "="*50)
    logger.info(f"遷移完成！")
    logger.info(f"總訂單數：{total_orders}")
    logger.info(f"已更新：{updated_orders}")
    logger.info(f"已跳過：{skipped_orders}")
    logger.info(f"="*50)

if __name__ == '__main__':
    print("開始遷移舊訂單...")
    print("此操作將為所有沒有 actualQuantity 字段的訂單添加此字段。")
    confirm = input("確認繼續嗎？(y/n): ")
    
    if confirm.lower() == 'y':
        migrate_orders()
    else:
        print("已取消")
