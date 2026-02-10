"""
路由：管理員後台 API
"""
from flask import Blueprint, request, jsonify, session
from auth import require_admin_login_api
from services.database_adapter import DatabaseAdapter
from services.line_service import LINEService
from datetime import datetime
import pytz
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


# ===== 會員管理 API =====

@admin_bp.route('/members', methods=['GET'])
@require_admin_login_api
def get_all_members():
    """取得所有會員列表"""
    try:
        members = DatabaseAdapter.get_all_members()
        return jsonify({
            "status": "success",
            "total": len(members),
            "members": members
        })
    except Exception as e:
        logger.error(f"Error in get_all_members: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/member/<user_id>', methods=['GET'])
@require_admin_login_api
def get_member(user_id):
    """取得單個會員資料"""
    try:
        member = DatabaseAdapter.get_member_by_id(user_id)
        if member:
            return jsonify({
                "status": "success",
                "member": member
            })
        else:
            return jsonify({
                "status": "error",
                "msg": "會員不存在"
            }), 404
    except Exception as e:
        logger.error(f"Error in get_member: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/member/update_status', methods=['POST'])
@require_admin_login_api
def update_member_status():
    """更新會員狀態"""
    try:
        data = request.json
        user_id = data.get('userId')
        status = data.get('status')
        
        if not user_id or not status:
            return jsonify({
                "status": "error",
                "msg": "缺少必要參數"
            }), 400
        
        success, message = DatabaseAdapter.update_member_status(user_id, status)
        
        if success:
            return jsonify({
                "status": "success",
                "msg": message
            })
        else:
            return jsonify({
                "status": "error",
                "msg": message
            }), 400
    except Exception as e:
        logger.error(f"Error in update_member_status: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/members/export', methods=['GET'])
@require_admin_login_api
def export_members():
    """導出會員資料為 CSV"""
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        members = DatabaseAdapter.get_all_members()
        
        # 建立 CSV 緩衝區
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'userId', 'name', 'phone', 'address', 'address2', 
            'birthDate', 'status', 'createdAt', 'updatedAt'
        ])
        
        writer.writeheader()
        for member in members:
            writer.writerow({
                'userId': member.get('userId', ''),
                'name': member.get('name', ''),
                'phone': member.get('phone', ''),
                'address': member.get('address', ''),
                'address2': member.get('address2', ''),
                'birthDate': member.get('birthDate', ''),
                'status': member.get('status', '啟用'),
                'createdAt': member.get('createdAt', ''),
                'updatedAt': member.get('updatedAt', '')
            })
        
        # 建立回應
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=members.csv"
        response.headers["Content-Type"] = "text/csv; charset=utf-8-sig"
        
        return response
    except Exception as e:
        logger.error(f"Error in export_members: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


# ===== 會員 ID 驗證工具 =====

@admin_bp.route('/member/generate_verification_token', methods=['POST'])
@require_admin_login_api
def generate_verification_token():
    """生成會員 ID 驗證令牌"""
    try:
        import secrets
        import json
        
        data = request.json
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({
                "status": "error",
                "msg": "缺少必要參數"
            }), 400
        
        member = DatabaseAdapter.get_member_by_id(user_id)
        if not member:
            return jsonify({
                "status": "error",
                "msg": "會員不存在"
            }), 404
        
        # 生成驗證令牌（隨機 32 位字符串）
        token = secrets.token_urlsafe(32)
        
        # 儲存令牌（實際應用中應存儲在緩存或資料庫中，有效期 24 小時）
        # 簡化版：存儲在 session 中
        session_key = f"verify_token_{token}"
        session[session_key] = {
            "userId": user_id,
            "timestamp": datetime.now(pytz.timezone('Asia/Taipei')).isoformat(),
            "membername": member.get('name', '')
        }
        
        logger.info(f"Verification token generated for user: {user_id}")
        
        return jsonify({
            "status": "success",
            "token": token,
            "msg": "驗證令牌生成成功"
        })
    except Exception as e:
        logger.error(f"Error in generate_verification_token: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/member/update_user_id', methods=['POST'])
@require_admin_login_api
def update_user_id():
    """手動更新會員 User ID"""
    try:
        import re
        
        data = request.json
        old_user_id = data.get('oldUserId')
        new_user_id = data.get('newUserId')
        
        if not old_user_id or not new_user_id:
            return jsonify({
                "status": "error",
                "msg": "缺少必要參數"
            }), 400
        
        # 驗證新 ID 格式
        line_id_pattern = r'^U[a-f0-9]{32}$'
        if not re.match(line_id_pattern, new_user_id, re.IGNORECASE):
            return jsonify({
                "status": "error",
                "msg": "無效的 LINE User ID 格式。格式應為：U + 32 個十六進制字符"
            }), 400
        
        # 檢查新 ID 是否已存在
        existing_member = DatabaseAdapter.get_member_by_id(new_user_id)
        if existing_member:
            return jsonify({
                "status": "error",
                "msg": "新的 User ID 已被其他會員使用"
            }), 400
        
        # 獲取舊會員資料
        old_member = DatabaseAdapter.get_member_by_id(old_user_id)
        if not old_member:
            return jsonify({
                "status": "error",
                "msg": "會員不存在"
            }), 404
        
        # 新增新 ID 的會員資料
        success = DatabaseAdapter.add_member(
            user_id=new_user_id,
            name=old_member.get('name'),
            phone=old_member.get('phone'),
            address=old_member.get('address'),
            birth_date=old_member.get('birthDate'),
            address2=old_member.get('address2')
        )
        
        if not success:
            return jsonify({
                "status": "error",
                "msg": "創建新記錄失敗"
            }), 500
        
        # 更新會員狀態為「停用」（保留舊 ID，防止重複）
        DatabaseAdapter.update_member_status(old_user_id, '停用')
        
        logger.info(f"User ID updated: {old_user_id} -> {new_user_id}")
        
        return jsonify({
            "status": "success",
            "msg": f"會員 ID 已更新。舊 ID ({old_user_id}) 已設為停用，新 ID ({new_user_id}) 已啟用"
        })
    except Exception as e:
        logger.error(f"Error in update_user_id: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500


@admin_bp.route('/webhook_logs', methods=['GET'])
@require_admin_login_api
def get_webhook_logs():
    """查看 Webhook 日誌"""
    try:
        user_id = request.args.get('userId')
        
        # 簡化版：返回模擬日誌
        # 實際應用應從資料庫查詢真實日誌
        logs = [
            {
                "timestamp": "2026-02-10 10:30:45",
                "event": "會員登入",
                "userId": user_id or "U*",
                "details": "用戶通過 LIFF 在 LINE 應用內登入"
            },
            {
                "timestamp": "2026-02-09 14:20:15",
                "event": "會員註冊",
                "userId": user_id or "U*",
                "details": "新用户完成註冊"
            }
        ]
        
        return jsonify({
            "status": "success",
            "logs": logs
        })
    except Exception as e:
        logger.error(f"Error in get_webhook_logs: {e}")
        return jsonify({
            "status": "error",
            "msg": str(e)
        }), 500