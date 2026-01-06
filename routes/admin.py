"""
路由：管理員後台 API
"""
from flask import Blueprint, request, jsonify, session
from auth import require_admin_login_api
from services.google_sheets import GoogleSheetsService
from services.line_service import LINEService
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/orders', methods=['GET'])
@require_admin_login_api
def get_all_orders():
    """取得所有訂單 (含會員資訊)"""
    try:
        orders = GoogleSheetsService.get_all_orders_with_members()
        return jsonify(orders)
    except Exception as e:
        logger.error(f"Error in get_all_orders: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/order/update_status', methods=['POST'])
@require_admin_login_api
def update_order_status():
    """更新訂單狀態"""
    try:
        data = request.json
        order_id = data.get('orderId')
        new_status = data.get('status')
        user_id = data.get('userId')
        
        if not order_id or not new_status:
            return jsonify({
                "status": "error",
                "msg": "缺少必要參數"
            }), 400
        
        success = GoogleSheetsService.update_order_status(order_id, new_status)
        
        if success:
            # 發送 LINE 通知
            if user_id:
                LINEService.send_status_update(user_id, order_id, new_status)
            
            return jsonify({"status": "success"})
        else:
            return jsonify({
                "status": "error",
                "msg": "訂單不存在"
            }), 404
    except Exception as e:
        logger.error(f"Error in update_order_status: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/order/update_payment', methods=['POST'])
@require_admin_login_api
def update_payment_status():
    """更新訂單付款狀態"""
    try:
        data = request.json
        order_id = data.get('orderId')
        payment_status = data.get('paymentStatus')
        
        if not order_id or not payment_status:
            return jsonify({
                "status": "error",
                "msg": "缺少必要參數"
            }), 400
        
        success = GoogleSheetsService.update_order_payment_status(order_id, payment_status)
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({
                "status": "error",
                "msg": "訂單不存在"
            }), 404
    except Exception as e:
        logger.error(f"Error in update_payment_status: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/order/add_delivery', methods=['POST'])
@require_admin_login_api
def add_delivery_log():
    """新增出貨紀錄"""
    try:
        data = request.json
        order_id = data.get('orderId')
        user_id = data.get('userId')
        qty = int(data.get('qty', 0))
        total_ordered = int(data.get('totalOrdered', 1))
        
        if not order_id or qty <= 0:
            return jsonify({
                "status": "error",
                "msg": "無效的參數"
            }), 400
        
        success, result = GoogleSheetsService.add_delivery_log(order_id, qty)
        
        if success:
            # 計算已配送數量
            orders = GoogleSheetsService.get_all_orders_with_members()
            current_order = next((o for o in orders if o['orderId'] == order_id), None)
            
            if current_order:
                total_delivered = sum(int(log['qty']) for log in current_order['deliveryLogs']) + qty
                # 發送 LINE 出貨通知
                LINEService.send_delivery_notification(user_id, qty, total_delivered, total_ordered, result)
            
            return jsonify({"status": "success"})
        else:
            return jsonify({
                "status": "error",
                "msg": result
            }), 400
    except Exception as e:
        logger.error(f"Error in add_delivery_log: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500
