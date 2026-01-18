"""
主應用程式入口 - 模組化結構
"""
from flask import Flask, render_template, request, session
import logging
import os
from datetime import timedelta
from config import Config
from services.google_sheets import GoogleSheetsService
from services.firestore_service import FirestoreService
from routes.auth import auth_bp
from routes.member import member_bp
from routes.admin import admin_bp
from routes.ecpay import ecpay_bp

# 配置日誌
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.INFO,
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 禁用 Werkzeug 日誌以改善啟動性能
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

# 建立 Flask 應用
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.debug = Config.DEBUG  # 設置 debug 模式

# 設置 Session 超時時間（180秒 = 3分鐘）
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=Config.SESSION_TIMEOUT)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# 開發環境使用 HTTP，生產環境使用 HTTPS
if Config.DEBUG:
    app.config['PREFERRED_URL_SCHEME'] = 'http'
else:
    app.config['PREFERRED_URL_SCHEME'] = 'https'

# 設置測試模式
import os
if os.environ.get('FLASK_ENV') == 'testing':
    app.testing = True

# 初始化資料庫服務
try:
    if Config.USE_FIRESTORE:
        FirestoreService.init()
        logger.info("Firebase Firestore initialized successfully")
    else:
        GoogleSheetsService.init()
        logger.info("Google Sheets initialized successfully")
    logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise

# 註冊藍圖
app.register_blueprint(auth_bp)
app.register_blueprint(member_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(ecpay_bp)


# ===== 前端路由 (頁面) =====

@app.route('/')
def home():
    """首頁"""
    return render_template('index.html')


@app.route('/admin')
def admin_page():
    """管理員後台"""
    from flask import session, redirect
    
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template('admin.html')


@app.route('/admin/products')
def admin_products_page():
    """商品管理頁面"""
    from flask import session, redirect
    
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template('admin_products.html')


@app.route('/admin/settings')
def admin_settings_page():
    """系統設定頁面 (分類、折扣、警告)"""
    from flask import session, redirect
    
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template('admin_settings.html')


@app.route('/admin/members')
def admin_members_page():
    """會員管理頁面"""
    from flask import session, redirect
    
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template('admin_settings.html')


@app.route('/admin/reports')
def admin_reports_page():
    """報表管理頁面"""
    from flask import session, redirect
    
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template('admin_reports.html')


# ===== 商品管理 API =====

@app.route('/api/admin/products', methods=['GET'])
def get_products():
    """取得所有商品"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, data = DatabaseAdapter.get_all_products()
        if success:
            return {"code": 0, "data": data}
        else:
            return {"code": 1, "message": data}, 400
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return {"code": 1, "message": "無法取得商品列表"}, 500


@app.route('/api/admin/product/add', methods=['POST'])
def add_product():
    """新增商品"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('unit') or not data.get('price') or not data.get('stock'):
            return {"code": 1, "message": "缺少必要欄位"}, 400
        
        success, result = DatabaseAdapter.add_product(
            name=data['name'],
            unit=data['unit'],
            price=float(data['price']),
            cost=float(data.get('cost', 0)),
            stock=int(data['stock']),
            min_stock_alert=int(data.get('minStockAlert', 0)) if data.get('minStockAlert') else 0,
            category_id=data.get('categoryId', ''),
            supplier_id=data.get('supplierId', ''),
            description=data.get('description', ''),
            image=data.get('image', '')
        )
        
        if success:
            return {"code": 0, "message": "商品新增成功", "data": result}
        else:
            return {"code": 1, "message": result}, 400
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        return {"code": 1, "message": "新增商品失敗"}, 500


@app.route('/api/admin/product/<product_id>', methods=['GET'])
def get_product(product_id):
    """取得特定商品"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, data = DatabaseAdapter.get_product(product_id)
        if success:
            return {"code": 0, "data": data}
        else:
            return {"code": 1, "message": data}, 400
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        return {"code": 1, "message": "無法取得商品資訊"}, 500


@app.route('/api/admin/product/<product_id>/update', methods=['POST'])
def update_product(product_id):
    """更新商品資訊"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        # 轉換數字類型
        if 'price' in data:
            data['price'] = float(data['price'])
        if 'cost' in data:
            data['cost'] = float(data['cost'])
        if 'stock' in data:
            data['stock'] = int(data['stock'])
        if 'minStockAlert' in data:
            data['minStockAlert'] = int(data['minStockAlert'])
        
        success, result = DatabaseAdapter.update_product(product_id, **data)
        
        if success:
            return {"code": 0, "message": "商品更新成功", "data": result}
        else:
            return {"code": 1, "message": result}, 400
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        return {"code": 1, "message": "更新商品失敗"}, 500


@app.route('/api/admin/product/<product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """刪除商品"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, message = DatabaseAdapter.delete_product(product_id)
        
        if success:
            return {"code": 0, "message": "商品已刪除"}
        else:
            return {"code": 1, "message": message}, 400
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        return {"code": 1, "message": "刪除商品失敗"}, 500


@app.route('/api/admin/product/<product_id>/stock', methods=['POST'])
def update_product_stock(product_id):
    """更新商品庫存"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        if not data or 'qtyChange' not in data or not data.get('reason'):
            return {"code": 1, "message": "缺少必要欄位"}, 400
        
        operator = session.get('admin_name', '系統')
        success, result = DatabaseAdapter.update_product_stock(
            product_id=product_id,
            qty_change=int(data['qtyChange']),
            reason=data['reason'],
            operator=operator
        )
        
        if success:
            return {"code": 0, "message": "庫存已更新", "data": result}
        else:
            return {"code": 1, "message": result}, 400
    except Exception as e:
        logger.error(f"Error updating product stock {product_id}: {e}")
        return {"code": 1, "message": "更新庫存失敗"}, 500


@app.route('/api/admin/stock-logs', methods=['GET'])
def get_stock_logs():
    """取得庫存日誌"""
    try:
        from services.database_adapter import DatabaseAdapter
        product_id = request.args.get('productId')
        limit = int(request.args.get('limit', 100))
        
        success, data = DatabaseAdapter.get_stock_logs(product_id, limit)
        if success:
            return {"code": 0, "data": data}
        else:
            return {"code": 1, "message": data}, 400
    except Exception as e:
        logger.error(f"Error fetching stock logs: {e}")
        return {"code": 1, "message": "無法取得庫存日誌"}, 500


@app.route('/api/admin/low-stock-products', methods=['GET'])
def get_low_stock_products():
    """取得低庫存商品"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, data = DatabaseAdapter.get_low_stock_products()
        if success:
            return {"code": 0, "data": data}
        else:
            return {"code": 1, "message": data}, 400
    except Exception as e:
        logger.error(f"Error fetching low stock products: {e}")
        return {"code": 1, "message": "無法取得低庫存商品"}, 500


# ===== HTTPS 強制 (生產環境) =====

@app.before_request
def enforce_https():
    """強制使用 HTTPS (在生產環境)"""
    # 在測試模式下不強制 HTTPS
    if app.testing:
        return
    
    # 在本地開發環境中不強制 HTTPS
    if app.debug:
        return
    
    # 檢查是否在代理後面 (X-Forwarded-Proto)
    if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        from flask import redirect
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)


@app.after_request
def set_security_headers(response):
    """設置安全頭"""
    # 在生產環境設置 HSTS
    if not app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # 移除開發環境的 HTTPS 強制
    else:
        # 確保開發環境不使用 HSTS
        if 'Strict-Transport-Security' in response.headers:
            del response.headers['Strict-Transport-Security']
    
    return response


# ===== 分類管理 API =====

@app.route('/api/admin/categories', methods=['GET'])
def get_categories():
    """取得所有分類"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, data = DatabaseAdapter.get_all_categories()
        return {
            "code": 0 if success else 1,
            "data": data,
            "message": "成功" if success else data
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/category/add', methods=['POST'])
def add_category():
    """新增分類"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        name = data.get('name', '')
        if not name:
            return {"code": 1, "message": "分類名稱不能為空"}, 400
        
        success, result = DatabaseAdapter.add_category(
            name=name,
            description=data.get('description', ''),
            color=data.get('color', ''),
            icon=data.get('icon', '')
        )
        return {
            "code": 0 if success else 1,
            "data": {"categoryId": result} if success else None,
            "message": "分類已新增" if success else result
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/category/<category_id>/update', methods=['POST'])
def update_category(category_id):
    """更新分類"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        success, message = DatabaseAdapter.update_category(category_id, **data)
        return {
            "code": 0 if success else 1,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/category/<category_id>/delete', methods=['POST'])
def delete_category(category_id):
    """刪除分類"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, message = DatabaseAdapter.delete_category(category_id)
        return {
            "code": 0 if success else 1,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


# ===== 折扣管理 API =====

@app.route('/api/admin/discounts', methods=['GET'])
def get_discounts():
    """取得所有折扣"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, data = DatabaseAdapter.get_all_discounts()
        return {
            "code": 0 if success else 1,
            "data": data,
            "message": "成功" if success else data
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/discount/add', methods=['POST'])
def add_discount():
    """新增折扣"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        name = data.get('name', '')
        discount_type = data.get('discountType', 'percentage')
        discount_value = data.get('discountValue', 0)
        
        if not name:
            return {"code": 1, "message": "折扣名稱不能為空"}, 400
        
        success, result = DatabaseAdapter.add_discount(
            name=name,
            discount_type=discount_type,
            discount_value=float(discount_value),
            target_type=data.get('targetType', 'product'),
            target_id=data.get('targetId'),
            start_date=data.get('startDate'),
            end_date=data.get('endDate'),
            description=data.get('description', '')
        )
        return {
            "code": 0 if success else 1,
            "data": {"discountId": result} if success else None,
            "message": "折扣已新增" if success else result
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/discount/<discount_id>/update', methods=['POST'])
def update_discount(discount_id):
    """更新折扣"""
    try:
        from services.database_adapter import DatabaseAdapter
        data = request.get_json()
        
        success, message = DatabaseAdapter.update_discount(discount_id, **data)
        return {
            "code": 0 if success else 1,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/discount/<discount_id>/delete', methods=['POST'])
def delete_discount(discount_id):
    """刪除折扣"""
    try:
        from services.database_adapter import DatabaseAdapter
        success, message = DatabaseAdapter.delete_discount(discount_id)
        return {
            "code": 0 if success else 1,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


# ===== 庫存警告 API =====

@app.route('/api/admin/stock-alerts', methods=['GET'])
def get_stock_alerts():
    """取得庫存警告"""
    try:
        from services.database_adapter import DatabaseAdapter
        status = request.args.get('status', 'active')
        alert_type = request.args.get('type')
        
        success, data = DatabaseAdapter.get_stock_alerts(status=status, alert_type=alert_type)
        return {
            "code": 0 if success else 1,
            "data": data,
            "message": "成功" if success else data
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


@app.route('/api/admin/stock-alert/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_stock_alert(alert_id):
    """確認庫存警告"""
    try:
        from services.database_adapter import DatabaseAdapter
        from flask import session
        
        operator = session.get('username', 'admin')
        success, message = DatabaseAdapter.acknowledge_stock_alert(alert_id, operator)
        return {
            "code": 0 if success else 1,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"code": 1, "message": str(e)}, 500


# ===== 錯誤處理 =====

@app.errorhandler(400)
def bad_request(error):
    """400 錯誤"""
    logger.warning(f"Bad request: {error}")
    return {"error": "請求格式不正確", "code": 400}, 400


@app.errorhandler(404)
def not_found(error):
    """404 錯誤"""
    return {"error": "頁面不存在", "code": 404}, 404


@app.errorhandler(500)
def internal_error(error):
    """500 錯誤"""
    logger.error(f"Internal server error: {error}")
    return {"error": "系統發生錯誤，請稍後重試", "code": 500}, 500


# ===== 管理員工具 (臨時操作用) =====

@app.route('/admin-tool/clear-all-data', methods=['POST'])
def admin_tool_clear_all_data():
    """
    清空所有 Firebase 數據 (臨時工具)
    需要驗證密碼
    """
    try:
        # 驗證密碼 (使用簡單的密鑰驗證)
        auth_key = request.headers.get('X-Admin-Key') or request.json.get('admin_key')
        
        # 簡單的密鑰驗證 (可在生產環境中改進)
        ADMIN_KEY = "admin_clear_2026"
        
        if not auth_key or auth_key != ADMIN_KEY:
            return {
                "status": "error",
                "msg": "未授權：需要有效的管理員密鑰"
            }, 401
        
        from services.firestore_service import FirestoreService
        
        collections_to_clear = [
            'orders',
            'members',
            'stockLogs',
            'categories',
            'discounts',
            'stockAlerts',
            'auditLogs',
            'products',
            'deliveryAppointments',
            'appointmentSlots',
        ]
        
        db = FirestoreService._db
        total_deleted = 0
        cleared_collections = {}
        
        for collection_name in collections_to_clear:
            try:
                docs = db.collection(collection_name).stream()
                doc_list = list(docs)
                
                if doc_list:
                    batch = db.batch()
                    for doc in doc_list:
                        batch.delete(doc.reference)
                    batch.commit()
                    total_deleted += len(doc_list)
                    cleared_collections[collection_name] = len(doc_list)
                else:
                    cleared_collections[collection_name] = 0
                    
            except Exception as e:
                cleared_collections[collection_name] = f"error: {str(e)[:50]}"
        
        logger.info(f"Admin cleared all data: {total_deleted} records deleted")
        
        return {
            "status": "success",
            "msg": f"所有數據已清空，刪除 {total_deleted} 筆紀錄",
            "total_deleted": total_deleted,
            "cleared_collections": cleared_collections
        }
        
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        return {
            "status": "error",
            "msg": str(e)
        }, 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    print(f"\n" + "="*60)
    print(f"🚀 應用已啟動於 http://0.0.0.0:{port}")
    print(f"   環境: {'開發' if Config.DEBUG else '生產'}")
    print(f"   使用虛擬環境: .venv")
    print(f"="*60 + "\n")
    
    # 啟動 Flask 應用
    app.run(
        debug=Config.DEBUG,  # 使用配置設置，允許開發環境使用 HTTP
        port=port,
        host='0.0.0.0',
        use_reloader=False,
        threaded=True
    )
