"""
資料遷移腳本 - 從 Google Sheets 遷移至 Firebase Firestore
使用前請確保：
1. Firebase 已初始化並配置正確
2. Firestore 資料庫已建立
3. 環境變數已設置
"""

import os
import sys
from datetime import datetime
import pytz
from config import Config
from services.google_sheets import GoogleSheetsService
from services.firestore_service import FirestoreService
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TW_TZ = pytz.timezone(Config.TIMEZONE)


def migrate_members():
    """遷移會員資料"""
    try:
        logger.info("開始遷移會員資料...")
        
        # 初始化服務
        GoogleSheetsService.init()
        FirestoreService.init()
        
        # 取得 Google Sheets 中的會員資料
        sheet = GoogleSheetsService.get_sheet("Members")
        if not sheet:
            logger.error("無法取得 Members 工作表")
            return False
        
        # 取得所有行 (跳過標題行)
        all_rows = sheet.get_all_values()
        if not all_rows:
            logger.warning("沒有會員資料要遷移")
            return True
        
        # 跳過標題行
        member_rows = all_rows[1:] if len(all_rows) > 1 else []
        
        migrated_count = 0
        for row in member_rows:
            if not row or not row[0]:  # 跳過空行
                continue
            
            try:
                user_id = row[0]
                name = row[1] if len(row) > 1 else ""
                phone = row[2] if len(row) > 2 else ""
                address = row[3] if len(row) > 3 else ""
                birth_date = row[4] if len(row) > 4 else ""
                address2 = row[5] if len(row) > 5 else ""
                
                # 寫入 Firestore
                FirestoreService.add_member(user_id, name, phone, address, birth_date, address2)
                migrated_count += 1
                logger.info(f"✓ 遷移會員: {user_id} - {name}")
            except Exception as e:
                logger.error(f"✗ 遷移會員失敗 {row[0]}: {e}")
                continue
        
        logger.info(f"會員資料遷移完成: {migrated_count} 筆")
        return True
    except Exception as e:
        logger.error(f"會員資料遷移失敗: {e}")
        return False


def migrate_orders():
    """遷移訂單資料"""
    try:
        logger.info("開始遷移訂單資料...")
        
        # 初始化服務
        GoogleSheetsService.init()
        FirestoreService.init()
        
        # 取得 Google Sheets 中的訂單資料
        sheet = GoogleSheetsService.get_sheet("Orders")
        if not sheet:
            logger.error("無法取得 Orders 工作表")
            return False
        
        # 取得所有行 (跳過標題行)
        all_rows = sheet.get_all_values()
        if not all_rows:
            logger.warning("沒有訂單資料要遷移")
            return True
        
        # 跳過標題行 (假設結構: 訂單ID, 用戶ID, 商品, 金額, 狀態, 付款狀態, 付款方式, 出貨日誌)
        order_rows = all_rows[1:] if len(all_rows) > 1 else []
        
        migrated_count = 0
        for row in order_rows:
            if not row or not row[0]:  # 跳過空行
                continue
            
            try:
                order_id = row[0]
                user_id = row[1] if len(row) > 1 else ""
                items = row[2] if len(row) > 2 else ""
                amount = float(row[3]) if len(row) > 3 and row[3] else 0
                status = row[4] if len(row) > 4 else ""
                payment_status = row[5] if len(row) > 5 else ""
                payment_method = row[6] if len(row) > 6 else ""
                
                # 出貨日誌需要特殊處理 (通常存儲為 JSON 或結構化資料)
                # 這裡假設存儲為空或簡單格式
                
                # 寫入 Firestore
                FirestoreService.add_order(
                    order_id,
                    user_id,
                    items,
                    amount,
                    status,
                    payment_status,
                    payment_method
                )
                migrated_count += 1
                logger.info(f"✓ 遷移訂單: {order_id}")
            except Exception as e:
                logger.error(f"✗ 遷移訂單失敗 {row[0]}: {e}")
                continue
        
        logger.info(f"訂單資料遷移完成: {migrated_count} 筆")
        return True
    except Exception as e:
        logger.error(f"訂單資料遷移失敗: {e}")
        return False


def verify_migration():
    """驗證遷移是否成功"""
    try:
        logger.info("\n開始驗證遷移結果...")
        
        GoogleSheetsService.init()
        FirestoreService.init()
        
        # 驗證會員數
        gs_members_sheet = GoogleSheetsService.get_sheet("Members")
        gs_members = len(gs_members_sheet.get_all_values()) - 1  # 減去標題行
        
        fs_members = len(FirestoreService._db.collection('members').stream())
        
        logger.info(f"Google Sheets 會員數: {gs_members}")
        logger.info(f"Firestore 會員數: {fs_members}")
        
        # 驗證訂單數
        gs_orders_sheet = GoogleSheetsService.get_sheet("Orders")
        gs_orders = len(gs_orders_sheet.get_all_values()) - 1  # 減去標題行
        
        fs_orders = len(FirestoreService._db.collection('orders').stream())
        
        logger.info(f"Google Sheets 訂單數: {gs_orders}")
        logger.info(f"Firestore 訂單數: {fs_orders}")
        
        # 檢查數據一致性
        if gs_members == fs_members and gs_orders == fs_orders:
            logger.info("✅ 驗證通過! 資料已完整遷移")
            return True
        else:
            logger.warning("⚠️  資料可能不完整，請檢查")
            return False
    except Exception as e:
        logger.error(f"驗證失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("資料遷移工具 - Google Sheets → Firebase Firestore")
    print("=" * 60)
    
    if not Config.USE_FIRESTORE:
        logger.warning("警告: 環境變數 USE_FIRESTORE 為 false")
        logger.warning("建議: 在遷移期間設置 USE_FIRESTORE=true")
        response = input("\n繼續遷移? (y/n): ")
        if response.lower() != 'y':
            logger.info("取消遷移")
            return
    
    # 執行遷移
    logger.info("\n開始資料遷移流程...\n")
    
    success = True
    success = migrate_members() and success
    success = migrate_orders() and success
    
    if success:
        logger.info("\n✅ 資料遷移完成!")
        verify_migration()
    else:
        logger.error("\n❌ 資料遷移出現錯誤，請檢查日誌")
        return 1
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"未預期的錯誤: {e}")
        sys.exit(1)
