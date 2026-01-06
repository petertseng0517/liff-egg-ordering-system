"""
主應用程式入口 - 模組化結構
"""
from flask import Flask, render_template, request
import logging
import os
from config import Config
from services.google_sheets import GoogleSheetsService
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

# 建立 Flask 應用
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# 開發環境使用 HTTP，生產環境使用 HTTPS
if Config.DEBUG:
    app.config['PREFERRED_URL_SCHEME'] = 'http'
else:
    app.config['PREFERRED_URL_SCHEME'] = 'https'

# 設置測試模式
import os
if os.environ.get('FLASK_ENV') == 'testing':
    app.testing = True

# 初始化 Google Sheets
try:
    GoogleSheetsService.init()
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


if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        port=int(os.getenv('PORT', 5005)),
        host='0.0.0.0'
    )

