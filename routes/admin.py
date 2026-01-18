"""
路由：管理員後台 API
"""
from flask import Blueprint, request, jsonify, session
from auth import require_admin_login_api
from services.database_adapter import DatabaseAdapter
from services.line_service import LINEService
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/orders', methods=['GET'])
@require_admin_login_api
def get_all_orders():
    """取得所有訂單 (含會員資訊)"""
    try:
        orders = DatabaseAdapter.get_all_orders_with_members()
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
        
        success = DatabaseAdapter.update_order_status(order_id, new_status)
        
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
        
        success = DatabaseAdapter.update_order_payment_status(order_id, payment_status)
        
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
        delivery_date = data.get('delivery_date', '')  # 客戶約定的出貨日期
        total_ordered = int(data.get('totalOrdered', 1))
        
        if not order_id or qty <= 0:
            return jsonify({
                "status": "error",
                "msg": "無效的參數"
            }), 400
        
        success, result = DatabaseAdapter.add_delivery_log(order_id, qty, address, delivery_date)
        
        if success:
            # result 已包含最新的狀態、總配送數量和出貨日期
            # 計算剩餘數量
            remaining_qty = total_ordered - result['total_delivered']
            
            # 發送 LINE 出貨通知
            LINEService.send_delivery_notification(
                user_id, order_id, result['delivery_date'], qty, remaining_qty
            )
            
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
        new_delivery_date = data.get('newDeliveryDate', '')
        reason = data.get('reason', '')
        old_qty = int(data.get('oldQty', 0))
        old_address = data.get('oldAddress', '')
        old_delivery_date = data.get('oldDeliveryDate', '')
        
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
        
        # 先修正出貨記錄
        success, delivery_result = DatabaseAdapter.correct_delivery_log(
            order_id, log_index, new_qty, new_address, new_delivery_date
        )
        
        if not success:
            return jsonify({
                "status": "error",
                "msg": delivery_result
            }), 400
        
        # 再添加審計日誌（以結構化的方式存儲）
        audit_success, audit_result = DatabaseAdapter.add_audit_log(
            order_id, "update_delivery", admin_name, 
            {"qty": old_qty, "address": old_address, "delivery_date": old_delivery_date},
            {"qty": new_qty, "address": new_address, "delivery_date": new_delivery_date},
            reason
        )
        
        if audit_success:
            # 發送 LINE 通知
            LINEService.send_delivery_correction_notification(
                user_id,
                order_id,
                '',
                old_qty,
                new_qty
            )
            
            return jsonify({
                "status": "success",
                "data": delivery_result
            })
        else:
            return jsonify({
                "status": "error",
                "msg": "審計日誌添加失敗"
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
        audit_logs = DatabaseAdapter.get_delivery_audit_logs(order_id)
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
        
        success = DatabaseAdapter.update_member(
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


@admin_bp.route('/clear-all-data', methods=['POST'])
@require_admin_login_api
def clear_all_data():
    """清空所有 Firebase 數據 (僅管理員可用)"""
    try:
        from services.firestore_service import FirestoreService
        
        # 要清空的集合列表
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
                    logger.info(f"Cleared {len(doc_list)} documents from {collection_name}")
            except Exception as e:
                logger.warning(f"Could not clear collection {collection_name}: {str(e)[:100]}")
        
        return jsonify({
            "status": "success",
            "msg": f"所有數據已清空，刪除 {total_deleted} 筆紀錄",
            "total_deleted": total_deleted
        })
    except Exception as e:
        logger.error(f"Error in clear_all_data: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


# ===== 報表相關 API =====

@admin_bp.route('/reports/delivery-records', methods=['GET'])
@require_admin_login_api
def get_delivery_records_report():
    """出貨單報表：根據出貨日期查詢所有出貨紀錄
    
    Query Parameters:
        delivery_date: YYYY-MM-DD 格式的出貨日期
    
    Response:
        {
            "status": "success",
            "delivery_date": "2026-01-20",
            "total_records": 3,
            "records": [
                {
                    "orderId": "ORD...",
                    "delivery_qty": 10,
                    "delivery_address": "新竹市...",
                    "customer_name": "范國紅",
                    "customer_phone": "0911351882"
                },
                ...
            ]
        }
    """
    try:
        delivery_date = request.args.get('delivery_date', '')
        
        if not delivery_date:
            return jsonify({
                "status": "error",
                "msg": "必須提供出貨日期 (delivery_date)"
            }), 400
        
        # 驗證日期格式
        try:
            from datetime import datetime
            datetime.strptime(delivery_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                "status": "error",
                "msg": "日期格式錯誤，應為 YYYY-MM-DD"
            }), 400
        
        # 取得所有訂單
        orders = DatabaseAdapter.get_all_orders_with_members()
        
        # 篩選符合出貨日期的出貨紀錄
        delivery_records = []
        for order in orders:
            if not order.get('deliveryLogs'):
                continue
            
            for delivery_log in order['deliveryLogs']:
                # 檢查該出貨紀錄的日期是否符合
                log_delivery_date = delivery_log.get('delivery_date', '')
                if log_delivery_date == delivery_date:
                    # 取得客戶資訊
                    customer = order.get('customer', {})
                    
                    # 計算實際出貨數量（使用修正後的數量或原始數量）
                    actual_qty = delivery_log.get('corrected_qty') or delivery_log.get('qty', 0)
                    
                    record = {
                        "orderId": order.get('orderId', ''),
                        "delivery_qty": actual_qty,
                        "delivery_address": delivery_log.get('address', ''),
                        "customer_name": customer.get('name', ''),
                        "customer_phone": customer.get('phone', '')
                    }
                    delivery_records.append(record)
        
        return jsonify({
            "status": "success",
            "delivery_date": delivery_date,
            "total_records": len(delivery_records),
            "records": delivery_records
        })
    except Exception as e:
        logger.error(f"Error in get_delivery_records_report: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500