#!/usr/bin/env python3
"""
Firebase Firestore 資料清除工具
這是一個CLI工具，用於安全地清除Firestore中的資料
只能在本地或授權環境中執行

使用方式：
    python clear_firestore_data.py                 # 清除所有資料（需確認）
    python clear_firestore_data.py --collection orders  # 清除特定集合
    python clear_firestore_data.py --help          # 查看幫助
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 所有可清除的集合
ALL_COLLECTIONS = [
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

# 受保護的集合（重要資料，需要額外確認）
PROTECTED_COLLECTIONS = [
    'members',
    'auditLogs',
]


class FirestoreCleaner:
    """Firestore資料清除工具"""
    
    def __init__(self):
        """初始化Firebase連線"""
        self.db = None
        self._init_firebase()
    
    def _init_firebase(self):
        """初始化Firebase"""
        try:
            if not firebase_admin._apps:
                # 從環境變數讀取配置
                creds_dict = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                }
                
                # 驗證必要的環境變數
                if not all([creds_dict['project_id'], creds_dict['private_key'], creds_dict['client_email']]):
                    raise ValueError("缺少必要的Firebase環境變數。請檢查.env檔案。")
                
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info("✅ Firebase Firestore 連線成功")
            logger.info(f"📦 Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
        except Exception as e:
            logger.error(f"❌ Firebase初始化失敗: {e}")
            sys.exit(1)
    
    def _confirm_action(self, message: str, is_protected: bool = False) -> bool:
        """獲取使用者確認"""
        if is_protected:
            # 受保護的集合需要額外確認
            print(f"\n⚠️  警告：這是受保護的資料集合")
            print(f"操作：{message}")
            print(f"請輸入 'yes, 我確定' 來確認此操作：")
            response = input("> ").strip()
            return response == "yes, 我確定"
        else:
            response = input(f"\n確認 {message}? (yes/no): ").strip().lower()
            return response == "yes"
    
    def clear_collection(self, collection_name: str, skip_confirm: bool = False) -> int:
        """清除指定集合中的所有文件"""
        if collection_name not in ALL_COLLECTIONS:
            logger.error(f"❌ 未知的集合: {collection_name}")
            logger.info(f"允許的集合: {', '.join(ALL_COLLECTIONS)}")
            return 0
        
        is_protected = collection_name in PROTECTED_COLLECTIONS
        
        # 獲取確認
        if not skip_confirm:
            message = f"清除集合 '{collection_name}'"
            if not self._confirm_action(message, is_protected):
                logger.info("❌ 操作已取消")
                return 0
        
        try:
            logger.info(f"🔄 正在清除集合: {collection_name}...")
            
            docs = self.db.collection(collection_name).stream()
            doc_list = list(docs)
            
            if not doc_list:
                logger.info(f"ℹ️  集合 '{collection_name}' 已為空")
                return 0
            
            # 分批刪除
            batch_size = 100
            total_deleted = 0
            
            for i in range(0, len(doc_list), batch_size):
                batch = self.db.batch()
                batch_docs = doc_list[i:i + batch_size]
                
                for doc in batch_docs:
                    batch.delete(doc.reference)
                
                batch.commit()
                total_deleted += len(batch_docs)
                logger.info(f"  已刪除 {total_deleted}/{len(doc_list)} 筆紀錄")
            
            logger.info(f"✅ 集合 '{collection_name}' 清除成功，共刪除 {total_deleted} 筆紀錄")
            return total_deleted
        
        except Exception as e:
            logger.error(f"❌ 清除集合 '{collection_name}' 失敗: {e}")
            return 0
    
    def clear_all(self, skip_confirm: bool = False) -> int:
        """清除所有集合"""
        if not skip_confirm:
            print(f"\n{'='*60}")
            print(f"🚨 警告：即將清除所有Firestore資料")
            print(f"{'='*60}")
            print(f"這將刪除以下集合中的所有文件：")
            for col in ALL_COLLECTIONS:
                print(f"  - {col}")
            print(f"\n此操作無法撤銷！")
            
            if not self._confirm_action("清除所有資料", is_protected=True):
                logger.info("❌ 操作已取消")
                return 0
        
        total_deleted = 0
        
        for collection_name in ALL_COLLECTIONS:
            deleted = self.clear_collection(collection_name, skip_confirm=True)
            total_deleted += deleted
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 所有資料清除完成，共刪除 {total_deleted} 筆紀錄")
        logger.info(f"{'='*60}")
        
        return total_deleted


def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description='Firebase Firestore 資料清除工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例：
  python clear_firestore_data.py                    # 清除所有資料
  python clear_firestore_data.py --collection orders  # 清除訂單集合
  python clear_firestore_data.py --list             # 列出所有可清除的集合
        '''
    )
    
    parser.add_argument(
        '--collection',
        type=str,
        help='指定要清除的集合名稱'
    )
    parser.add_argument(
        '--skip-confirm',
        action='store_true',
        help='跳過確認提示（謹慎使用！）'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有可清除的集合'
    )
    
    args = parser.parse_args()
    
    # 列出所有集合
    if args.list:
        print(f"\n可清除的集合列表：")
        for i, col in enumerate(ALL_COLLECTIONS, 1):
            protected = " (🔒 受保護)" if col in PROTECTED_COLLECTIONS else ""
            print(f"  {i}. {col}{protected}")
        return
    
    # 初始化清除工具
    cleaner = FirestoreCleaner()
    
    # 清除特定集合或全部
    if args.collection:
        cleaner.clear_collection(args.collection, skip_confirm=args.skip_confirm)
    else:
        cleaner.clear_all(skip_confirm=args.skip_confirm)


if __name__ == '__main__':
    main()
