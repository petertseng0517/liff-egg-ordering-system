"""
路由：ECPay 金流回調
"""
from flask import Blueprint, request
from services.google_sheets import GoogleSheetsService
from services.line_service import LINEService
from ecpay_sdk import ECPaySDK
from config import Config
import logging
import os

logger = logging.getLogger(__name__)

ecpay_bp = Blueprint('ecpay', __name__, url_prefix='/api/ecpay')


@ecpay_bp.route('/callback', methods=['POST'])
def ecpay_callback():
    """ECPay 伺服器回調"""
    try:
        data = request.form.to_dict()
        logger.info(f"ECPay Callback Received: {data}")
        
        # 驗證 CheckMacValue
        received_check_mac = data.get('CheckMacValue')
        if not received_check_mac:
            logger.warning("No CheckMacValue in callback")
            return '0|No CheckMacValue'
        
        ecpay_service = ECPaySDK(
            Config.ECPAY_MERCHANT_ID,
            Config.ECPAY_HASH_KEY,
            Config.ECPAY_HASH_IV,
            Config.ECPAY_ACTION_URL
        )
        
        calculated_check_mac = ecpay_service.generate_check_mac_value(data)
        
        if received_check_mac != calculated_check_mac:
            logger.error(f"Checksum Invalid. Received: {received_check_mac}, Calculated: {calculated_check_mac}")
            return '0|CheckSum Invalid'
        
        # 檢查付款結果
        rtn_code = data.get('RtnCode')
        if rtn_code == '1':
            order_id = data.get('MerchantTradeNo')
            logger.info(f"Payment Success for Order: {order_id}")
            
            # 更新付款狀態
            success = GoogleSheetsService.update_order_payment_status(order_id, "已付款")
            
            if success:
                # 取得使用者信息並發送 LINE 通知
                orders = GoogleSheetsService.get_all_orders_with_members()
                order = next((o for o in orders if o['orderId'] == order_id), None)
                
                if order:
                    LINEService.send_payment_success(order['userId'], order_id)
                
                logger.info(f"Order {order_id} marked as paid")
                return '1|OK'
            else:
                logger.warning(f"Order {order_id} not found or update failed")
                return '0|Error'
        else:
            logger.warning(f"Payment Failed. RtnCode: {rtn_code}, Msg: {data.get('RtnMsg')}")
            return '1|OK'
    except Exception as e:
        logger.error(f"Error in ecpay_callback: {e}")
        return '0|Error'


@ecpay_bp.route('/client_return', methods=['GET', 'POST'])
def ecpay_client_return():
    """ECPay 用戶返回導向"""
    try:
        from flask import redirect
        logger.info("User redirected from ECPay payment")
        return redirect('/?page=history')
    except Exception as e:
        logger.error(f"Error in ecpay_client_return: {e}")
        return redirect('/')
