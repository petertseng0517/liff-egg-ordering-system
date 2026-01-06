"""
LINE Messaging Service 模組
"""
import logging
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)
from config import Config

logger = logging.getLogger(__name__)


class LINEService:
    """LINE 訊息推播服務"""
    
    @staticmethod
    def send_push_message(user_id, text):
        """推送訊息給使用者"""
        if not Config.LINE_CHANNEL_ACCESS_TOKEN or \
           Config.LINE_CHANNEL_ACCESS_TOKEN == 'YOUR_CHANNEL_ACCESS_TOKEN':
            logger.warning("LINE token not configured, skipping push message")
            return False
        
        if not user_id:
            logger.warning("User ID is empty")
            return False
        
        try:
            configuration = Configuration(access_token=Config.LINE_CHANNEL_ACCESS_TOKEN)
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                push_message_request = PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=text)]
                )
                line_bot_api.push_message(push_message_request)
                logger.info(f"Push message sent to {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error sending push message: {e}")
            return False
    
    @staticmethod
    def send_order_confirmation(user_id, order_id, item_str, amount, payment_status):
        """發送訂單確認訊息"""
        msg = (
            f"✅ 訂單已送出\n"
            f"訂單編號: {order_id}\n"
            f"商品: {item_str}\n"
            f"總金額: ${amount}\n"
            f"付款狀態: {payment_status}\n"
            f"\n我們將盡快處理您的訂單！"
        )
        return LINEService.send_push_message(user_id, msg)
    
    @staticmethod
    def send_payment_success(user_id, order_id):
        """發送付款成功訊息"""
        msg = f"💰 付款成功通知\n訂單 {order_id} 已收到您的付款，感謝！"
        return LINEService.send_push_message(user_id, msg)
    
    @staticmethod
    def send_delivery_notification(user_id, qty, total_delivered, total_ordered, status):
        """發送出貨通知訊息"""
        msg = f"📦 出貨通知\n您好，我們已為您出貨 {qty} 盤土雞蛋。\n目前進度: {total_delivered}/{total_ordered} 盤。"
        
        if status == "已完成":
            msg += "\n🎉 您的訂單已全數出貨完畢，感謝您的訂購！"
        else:
            msg += "\n其餘商品將盡快安排配送。"
        
        return LINEService.send_push_message(user_id, msg)
    
    @staticmethod
    def send_status_update(user_id, order_id, new_status):
        """發送狀態更新訊息"""
        msg_map = {
            "已確認": "您的訂單已確認，我們將盡快安排。",
            "配送中": "您的蛋已經出發囉！請留意電話。",
            "已完成": "訂單已完成，感謝您的購買！"
        }
        msg = msg_map.get(new_status, f"您的訂單狀態已更新為：{new_status}")
        return LINEService.send_push_message(user_id, msg)
