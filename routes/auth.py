"""
路由：身份驗證與登入
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from auth import login_tracker, Config
from config import Config as AppConfig
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """管理員登入"""
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        client_ip = request.remote_addr
        
        # 檢查是否被鎖定
        if login_tracker.is_locked(client_ip):
            remaining_time = login_tracker.get_remaining_time(client_ip)
            error_msg = f"登入嘗試過多，請在 {remaining_time} 秒後重試"
            logger.warning(f"Login attempt locked for IP {client_ip}")
            return render_template('login.html', error=error_msg), 429
        
        # 驗證密碼
        if not password:
            login_tracker.record_attempt(client_ip)
            return render_template('login.html', error="密碼不能為空")
        
        if password == AppConfig.ADMIN_PASSWORD:
            session['logged_in'] = True
            login_tracker.reset(client_ip)
            logger.info(f"Admin login successful from IP {client_ip}")
            return redirect(url_for('admin_page'))
        else:
            login_tracker.record_attempt(client_ip)
            attempts_left = AppConfig.MAX_LOGIN_ATTEMPTS - login_tracker.attempts.get(
                login_tracker.get_key(client_ip),
                {'count': 0}
            )['count']
            error_msg = f"密碼錯誤 (剩餘嘗試次數: {max(0, attempts_left)})"
            logger.warning(f"Failed login attempt from IP {client_ip}")
            return render_template('login.html', error=error_msg)
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """登出"""
    session.pop('logged_in', None)
    logger.info(f"Admin logged out from IP {request.remote_addr}")
    return redirect(url_for('auth.login'))
