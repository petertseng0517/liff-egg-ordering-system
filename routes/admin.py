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
        address = data.get('address', '')
        total_ordered = int(data.get('totalOrdered', 1))
        
        if not order_id or qty <= 0:
            return jsonify({
                "status": "error",
                "msg": "無效的參數"
            }), 400
        
        success, result = GoogleSheetsService.add_delivery_log(order_id, qty, address)
        
        if success:
            # result 已包含最新的狀態和總配送數量，無需再查詢
            # 發送 LINE 出貨通知
            if isinstance(result, dict) and 'total_delivered' in result:
                LINEService.send_delivery_notification(user_id, qty, result['total_delivered'], total_ordered, order_id)
            else:
                # 向後相容性：如果是舊格式，則發送基本通知
                LINEService.send_delivery_notification(user_id, qty, qty, total_ordered, order_id)
            
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

@admin_bp.route('/order/correct_delivery', methods=['POST'])
@require_admin_login_api
def correct_delivery_log():
    """修正出貨紀錄"""
    try:
        data = request.json
        order_id = data.get('orderId')
        user_id = data.get('userId')
        log_index = int(data.get('logIndex', -1))
        new_qty = int(data.get('newQty', 0))
        new_address = data.get('newAddress', '')
        reason = data.get('reason', '')
        
        # 獲取管理者名稱
        admin_name = session.get('user_name', 'unknown')
        
        if not order_id or log_index < 0 or new_qty <= 0:
            return jsonify({
                "status": "error",
                "msg": "無效的參數"
            }), 400
        
        if not reason:
            return jsonify({
                "status": "error",
                "msg": "必須提供修正原因"
            }), 400
        
        success, result = GoogleSheetsService.correct_delivery_log(
            order_id, log_index, new_qty, new_address, admin_name, reason
        )
        
        if success:
            # 結果已包含修正後的 total_delivered 和 total_ordered
            LINEService.send_delivery_correction_notification(
                user_id, 
                result['old_qty'],
                result['new_qty'],
                reason,
                result.get('total_delivered', 0),
                result.get('total_ordered', 1),
                result['status']
            )
            
            return jsonify({
                "status": "success",
                "data": result
            })
        else:
            return jsonify({
                "status": "error",
                "msg": result
            }), 400
    except Exception as e:
        logger.error(f"Error in correct_delivery_log: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/order/delivery_audit/<order_id>', methods=['GET'])
@require_admin_login_api
def get_delivery_audit(order_id):
    """獲取出貨修正審計日誌"""
    try:
        audit_logs = GoogleSheetsService.get_delivery_audit_logs(order_id)
        return jsonify(audit_logs)
    except Exception as e:
        logger.error(f"Error in get_delivery_audit: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500

@admin_bp.route('/member/update', methods=['POST'])
@require_admin_login_api
def update_member():
    """更新會員資料"""
    try:
        data = request.json
        user_id = data.get('userId')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        address2 = data.get('address2', '').strip()
        
        # 驗證必填項
        if not user_id or not name or not phone or not address:
            return jsonify({
                "status": "error",
                "msg": "缺少必要資訊"
            }), 400
        
        success = GoogleSheetsService.update_member(
            user_id, name, phone, address, address2
        )
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({
                "status": "error",
                "msg": "會員不存在或更新失敗"
            }), 404
    except Exception as e:
        logger.error(f"Error in update_member: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500