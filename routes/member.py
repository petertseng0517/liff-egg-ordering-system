"""
路由：會員與訂單相關 API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from services.google_sheets import GoogleSheetsService
from services.line_service import LINEService
from validation import FormValidator
from config import ProductConfig
from ecpay_sdk import ECPaySDK
import os
import logging
import pytz

logger = logging.getLogger(__name__)

member_bp = Blueprint('member', __name__, url_prefix='/api')


@member_bp.route('/check_member', methods=['POST'])
def check_member():
    """檢查會員是否存在"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({"error": "userId required"}), 400
        
        member = GoogleSheetsService.check_member_exists(user_id)
        
        if member:
            return jsonify({
                "registered": True,
                "name": member.get('name', ''),
                "data": member
            })
        else:
            return jsonify({"registered": False})
    except Exception as e:
        logger.error(f"Error checking member: {e}")
        return jsonify({"error": str(e)}), 500


@member_bp.route('/register', methods=['POST'])
def register():
    """新增會員"""
    try:
        data = request.json
        
        # 表單驗證
        validation_errors = FormValidator.validate_register_form(data)
        if validation_errors:
            return jsonify({
                "status": "error",
                "msg": "表單驗證失敗",
                "errors": validation_errors
            }), 400
        
        # 新增會員
        success = GoogleSheetsService.add_member(
            user_id=data.get('userId'),
            name=data.get('name').strip(),
            phone=data.get('phone').strip(),
            address=data.get('address').strip(),
            birth_date=data.get('birthDate', '').strip(),
            address2=data.get('address2', '').strip()
        )
        
        if success:
            return jsonify({"status": "success", "msg": "註冊成功"})
        else:
            return jsonify({
                "status": "error",
                "msg": "註冊失敗，請稍後重試"
            }), 500
    except Exception as e:
        logger.error(f"Error in register: {e}")
        return jsonify({"status": "error", "msg": "系統錯誤"}), 500


@member_bp.route('/edit_member', methods=['POST'])
def edit_member():
    """編輯會員資料"""
    try:
        data = request.json
        user_id = data.get('userId')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        address2 = data.get('address2', '').strip()
        
        # 驗證
        if not user_id or not name or not phone or not address:
            return jsonify({
                "status": "error",
                "msg": "缺少必要信息"
            }), 400
        
        # 更新會員資料
        success = GoogleSheetsService.update_member(
            user_id=user_id,
            name=name,
            phone=phone,
            address=address,
            address2=address2
        )
        
        if success:
            return jsonify({"status": "success", "msg": "會員資料已更新"})
        else:
            return jsonify({
                "status": "error",
                "msg": "會員不存在或更新失敗"
            }), 404
    except Exception as e:
        logger.error(f"Error in edit_member: {e}")
        return jsonify({"status": "error", "msg": "系統錯誤"}), 500


@member_bp.route('/order', methods=['POST'])
def create_order():
    """建立訂單"""
    try:
        data = request.json
        
        # 表單驗證
        validation_errors = FormValidator.validate_order_form(data)
        if validation_errors:
            return jsonify({
                "status": "error",
                "msg": "表單驗證失敗",
                "errors": validation_errors
            }), 400
        
        user_id = data.get('userId')
        item_name = data.get('itemName')
        qty = int(data.get('qty', 1))
        remarks = data.get('remarks', '').strip()
        payment_method = data.get('paymentMethod', 'transfer')
        
        # 驗證商品
        if item_name not in ProductConfig.PRODUCTS:
            return jsonify({
                "status": "error",
                "msg": "商品不存在"
            }), 400
        
        # 計算價格
        unit_price = ProductConfig.get_unit_price(item_name, qty)
        total_amount = unit_price * qty
        
        # 生成訂單
        order_id = "ORD" + str(int(datetime.now(pytz.timezone('Asia/Taipei')).timestamp()))
        
        # 正規化商品名稱與數量
        actual_item_name = item_name
        actual_qty = qty
        
        if item_name == "土雞蛋11盤":
            actual_qty = qty * 11
            actual_item_name = "土雞蛋(11盤優惠組)"
        elif item_name == "土雞蛋1盤":
            actual_qty = qty
            actual_item_name = "土雞蛋"
        
        # 組合商品字串
        item_str = f"{actual_item_name} x{actual_qty}"
        if remarks:
            item_str += f" ({remarks})"
        
        # 設定初始付款狀態
        initial_payment_status = "待付款" if payment_method == 'ecpay' else "未付款"
        
        # 新增訂單
        success = GoogleSheetsService.add_order(
            order_id=order_id,
            user_id=user_id,
            item_str=item_str,
            amount=total_amount,
            status="處理中",
            payment_status=initial_payment_status,
            payment_method=payment_method
        )
        
        if not success:
            return jsonify({
                "status": "error",
                "msg": "訂單建立失敗"
            }), 500
        
        # 發送 LINE 確認訊息
        LINEService.send_order_confirmation(user_id, order_id, item_str, total_amount, initial_payment_status)
        
        # ECPay 付款
        if payment_method == 'ecpay':
            base_url = os.getenv('APP_BASE_URL')
            if not base_url:
                base_url = request.url_root.rstrip('/')
                if 'onrender.com' in base_url or 'herokuapp.com' in base_url:
                    base_url = base_url.replace('http://', 'https://')
            else:
                base_url = base_url.rstrip('/')
            
            return_url = f"{base_url}/api/ecpay/callback"
            client_back_url = f"{base_url}/api/ecpay/client_return"
            
            ecpay_service = ECPaySDK(
                os.getenv('ECPAY_MERCHANT_ID', '2000132'),
                os.getenv('ECPAY_HASH_KEY', '5294y06JbISpM5x9'),
                os.getenv('ECPAY_HASH_IV', 'v77hoKGq4kWxNNIS'),
                'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'
            )
            
            ecpay_params = ecpay_service.create_order(
                order_id=order_id,
                total_amount=total_amount,
                item_name=item_name,
                return_url=return_url,
                client_back_url=client_back_url,
                order_result_url=""
            )
            
            return jsonify({
                "status": "ecpay_init",
                "msg": "前往綠界付款",
                "orderId": order_id,
                "ecpayParams": ecpay_params,
                "actionUrl": 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'
            })
        
        return jsonify({
            "status": "success",
            "msg": "訂購成功",
            "orderId": order_id
        })
    except Exception as e:
        logger.error(f"Error in create_order: {e}")
        return jsonify({
            "status": "error",
            "msg": "系統錯誤"
        }), 500


@member_bp.route('/history', methods=['POST'])
def get_history():
    """取得訂購紀錄"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({"error": "userId required"}), 400
        
        orders = GoogleSheetsService.get_user_orders(user_id)
        return jsonify(orders)
    except Exception as e:
        logger.error(f"Error in get_history: {e}")
        return jsonify({"error": str(e)}), 500


@member_bp.route('/retry_payment', methods=['POST'])
def retry_payment():
    """重新初始化 ECPay 付款流程"""
    try:
        data = request.json
        order_id = data.get('orderId')
        retry_count = data.get('retryCount', 1)  # 第幾次重試
        
        if not order_id:
            return jsonify({"status": "error", "msg": "訂單 ID 不存在"}), 400
        
        # 取得訂單信息
        orders = GoogleSheetsService.get_all_orders_with_members()
        order = next((o for o in orders if o['orderId'] == order_id), None)
        
        if not order:
            return jsonify({"status": "error", "msg": "訂單不存在"}), 404
        
        # 確認是未付款狀態
        if order['paymentStatus'] not in ['未付款', '待付款']:
            return jsonify({"status": "error", "msg": "訂單已付款，無需重新付款"}), 400
        
        # 為 ECPay 生成新的交易編號（含重試次數）
        # 格式：ORD1234567890_retry_1, ORD1234567890_retry_2 ...
        ecpay_trade_no = f"{order_id}_retry_{retry_count}"
        amount = int(order['amount'])
        
        base_url = os.getenv('APP_BASE_URL')
        if not base_url:
            base_url = request.url_root.rstrip('/')
            if 'onrender.com' in base_url or 'herokuapp.com' in base_url:
                base_url = base_url.replace('http://', 'https://')
        else:
            base_url = base_url.rstrip('/')
        
        return_url = f"{base_url}/api/ecpay/callback"
        client_back_url = f"{base_url}/api/ecpay/client_return"
        
        ecpay_service = ECPaySDK(
            os.getenv('ECPAY_MERCHANT_ID', '2000132'),
            os.getenv('ECPAY_HASH_KEY', '5294y06JbISpM5x9'),
            os.getenv('ECPAY_HASH_IV', 'v77hoKGq4kWxNNIS'),
            'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'
        )
        
        ecpay_params = ecpay_service.create_order(
            order_id=ecpay_trade_no,  # ⭐ 使用新的交易編號（含 _retry_ 後綴）
            total_amount=amount,
            item_name=order['items'],
            return_url=return_url,
            client_back_url=client_back_url,
            order_result_url=""
        )
        
        logger.info(f"Retry payment for order {order_id}, ECPay Trade No: {ecpay_trade_no}")
        return jsonify({
            "status": "ecpay_init",
            "actionUrl": 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5',
            "ecpayParams": ecpay_params
        })
    
    except Exception as e:
        logger.error(f"Error in retry_payment: {e}")
        return jsonify({"status": "error", "msg": "系統錯誤"}), 500
