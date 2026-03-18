"""
單元測試 - Firebase Firestore Service (services/firestore_service.py)
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.firestore_service import FirestoreService


def make_mock_db():
    """建立標準 Firestore mock db"""
    db = MagicMock()
    FirestoreService._db = db
    return db


class TestAddMember(unittest.TestCase):

    def test_success(self):
        db = make_mock_db()
        result = FirestoreService.add_member('U123', '王小明', '0912345678', '新竹市')
        self.assertTrue(result)
        db.collection.assert_called_with('members')

    def test_with_optional_fields(self):
        make_mock_db()
        result = FirestoreService.add_member(
            'U123', '王小明', '0912345678', '新竹市',
            birth_date='1990-01-15', address2='公司地址'
        )
        self.assertTrue(result)

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.add_member('U123', '王小明', '0912345678', '新竹市')
        self.assertFalse(result)


class TestCheckMemberExists(unittest.TestCase):

    def test_member_exists_returns_dict(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'userId': 'U123', 'name': '王小明',
            'phone': '0912345678', 'address': '新竹市',
            'birthDate': '1990-01-15', 'address2': ''
        }
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        result = FirestoreService.check_member_exists('U123')
        self.assertIsNotNone(result)
        self.assertEqual(result['userId'], 'U123')
        self.assertEqual(result['name'], '王小明')

    def test_member_not_exists_returns_none(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        result = FirestoreService.check_member_exists('U999')
        self.assertIsNone(result)

    def test_db_exception_returns_none(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.check_member_exists('U123')
        self.assertIsNone(result)


class TestUpdateMember(unittest.TestCase):

    def test_success(self):
        db = make_mock_db()
        result = FirestoreService.update_member('U123', '王大明', '0987654321', '竹北市', '辦公室')
        self.assertTrue(result)
        db.collection.assert_called_with('members')

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.update_member('U123', '王大明', '0987654321', '竹北市')
        self.assertFalse(result)


class TestGetAllMembers(unittest.TestCase):

    def test_returns_members_list(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            'userId': 'U123', 'name': '王小明',
            'createdAt': '2026-01-01', 'updatedAt': '2026-01-01'
        }
        db.collection.return_value.stream.return_value = [mock_doc]
        result = FirestoreService.get_all_members()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['userId'], 'U123')

    def test_adds_default_status_if_missing(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            'userId': 'U123', 'name': '王小明',
            'createdAt': None, 'updatedAt': None
        }
        db.collection.return_value.stream.return_value = [mock_doc]
        result = FirestoreService.get_all_members()
        self.assertEqual(result[0]['status'], '啟用')

    def test_converts_timestamp_to_string(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        fake_ts = MagicMock()
        fake_ts.strftime.return_value = '2026-01-01 00:00:00'
        mock_doc.to_dict.return_value = {
            'userId': 'U123', 'name': '王小明',
            'createdAt': fake_ts, 'updatedAt': fake_ts
        }
        db.collection.return_value.stream.return_value = [mock_doc]
        result = FirestoreService.get_all_members()
        self.assertEqual(result[0]['createdAt'], '2026-01-01 00:00:00')

    def test_db_exception_returns_empty_list(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.get_all_members()
        self.assertEqual(result, [])


class TestGetMemberById(unittest.TestCase):

    def test_found_returns_true_and_data(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'userId': 'U123', 'name': '王小明'}
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, data = FirestoreService.get_member_by_id('U123')
        self.assertTrue(success)
        self.assertEqual(data['name'], '王小明')

    def test_not_found_returns_false_and_message(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, msg = FirestoreService.get_member_by_id('U999')
        self.assertFalse(success)
        self.assertEqual(msg, '會員不存在')

    def test_adds_default_status_if_missing(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'userId': 'U123', 'name': '王小明'}
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, data = FirestoreService.get_member_by_id('U123')
        self.assertEqual(data['status'], '啟用')

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        success, msg = FirestoreService.get_member_by_id('U123')
        self.assertFalse(success)


class TestUpdateMemberStatus(unittest.TestCase):

    def test_valid_status_success(self):
        make_mock_db()
        success, msg = FirestoreService.update_member_status('U123', '停用')
        self.assertTrue(success)
        self.assertEqual(msg, '狀態更新成功')

    def test_all_valid_statuses(self):
        make_mock_db()
        for status in ['啟用', '停用', '黑名單']:
            success, _ = FirestoreService.update_member_status('U123', status)
            self.assertTrue(success, f"狀態 '{status}' 應該有效")

    def test_invalid_status_returns_false(self):
        make_mock_db()
        success, msg = FirestoreService.update_member_status('U123', '無效狀態')
        self.assertFalse(success)
        self.assertIn('無效', msg)

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        success, msg = FirestoreService.update_member_status('U123', '停用')
        self.assertFalse(success)


class TestAddOrder(unittest.TestCase):

    def test_success(self):
        db = make_mock_db()
        result = FirestoreService.add_order(
            'ORD001', 'U123', '土雞蛋 x5', 500,
            '待確認', '未付款', 'transfer'
        )
        self.assertTrue(result)
        db.collection.assert_called_with('orders')

    def test_with_optional_fields(self):
        make_mock_db()
        result = FirestoreService.add_order(
            'ORD001', 'U123', '土雞蛋 x5', 500,
            '待確認', '未付款', 'transfer',
            product_id='prod_001', actual_quantity=6, order_qty=5
        )
        self.assertTrue(result)

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.add_order(
            'ORD001', 'U123', '土雞蛋 x5', 500, '待確認', '未付款', 'transfer'
        )
        self.assertFalse(result)


class TestGetAllOrdersWithMembers(unittest.TestCase):

    def test_joins_member_data_to_orders(self):
        db = make_mock_db()
        member_doc = MagicMock()
        member_doc.id = 'U123'
        member_doc.to_dict.return_value = {'userId': 'U123', 'name': '王小明'}

        order_doc = MagicMock()
        order_doc.to_dict.return_value = {
            'orderId': 'ORD001', 'userId': 'U123',
            'date': '2026-03-18 10:00:00'
        }

        def collection_side(name):
            mock = MagicMock()
            if name == 'members':
                mock.stream.return_value = [member_doc]
            elif name == 'orders':
                mock.stream.return_value = [order_doc]
            return mock

        db.collection.side_effect = collection_side
        result = FirestoreService.get_all_orders_with_members()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['customer']['name'], '王小明')

    def test_order_with_no_member_gets_empty_customer(self):
        db = make_mock_db()
        member_doc = MagicMock()
        member_doc.id = 'U999'
        member_doc.to_dict.return_value = {'userId': 'U999', 'name': '其他人'}

        order_doc = MagicMock()
        order_doc.to_dict.return_value = {
            'orderId': 'ORD001', 'userId': 'U123',
            'date': '2026-03-18 10:00:00'
        }

        def collection_side(name):
            mock = MagicMock()
            if name == 'members':
                mock.stream.return_value = [member_doc]
            elif name == 'orders':
                mock.stream.return_value = [order_doc]
            return mock

        db.collection.side_effect = collection_side
        result = FirestoreService.get_all_orders_with_members()
        self.assertEqual(result[0]['customer'], {})

    def test_db_exception_returns_empty_list(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.get_all_orders_with_members()
        self.assertEqual(result, [])


class TestAddDeliveryLog(unittest.TestCase):

    def _setup_order(self, db, order_data):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = order_data
        db.collection.return_value.document.return_value.get.return_value = mock_doc

    def test_partial_delivery_sets_correct_status(self):
        db = make_mock_db()
        self._setup_order(db, {
            'deliveryLogs': [],
            'orderQty': 10, 'actualQuantity': 1
        })
        success, result = FirestoreService.add_delivery_log('ORD001', 5, '新竹市', '2026-03-18')
        self.assertTrue(success)
        self.assertEqual(result['status'], '部分配送')
        self.assertEqual(result['total_delivered'], 5)

    def test_full_delivery_sets_completed_status(self):
        db = make_mock_db()
        self._setup_order(db, {
            'deliveryLogs': [],
            'orderQty': 5, 'actualQuantity': 1
        })
        success, result = FirestoreService.add_delivery_log('ORD001', 5, '新竹市', '2026-03-18')
        self.assertTrue(success)
        self.assertEqual(result['status'], '已完成')

    def test_order_not_found_returns_false(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, msg = FirestoreService.add_delivery_log('ORD999', 5)
        self.assertFalse(success)
        self.assertEqual(msg, '訂單不存在')

    def test_legacy_order_format_backward_compatible(self):
        db = make_mock_db()
        self._setup_order(db, {
            'deliveryLogs': [],
            'items': '土雞蛋 x5'  # 舊格式
        })
        success, result = FirestoreService.add_delivery_log('ORD001', 5)
        self.assertTrue(success)
        self.assertEqual(result['status'], '已完成')

    def test_uses_delivery_date_when_provided(self):
        db = make_mock_db()
        self._setup_order(db, {
            'deliveryLogs': [],
            'orderQty': 10, 'actualQuantity': 1
        })
        success, result = FirestoreService.add_delivery_log('ORD001', 5, '新竹市', '2026-03-20')
        self.assertTrue(success)
        self.assertEqual(result['delivery_date'], '2026-03-20')


class TestCorrectDeliveryLog(unittest.TestCase):

    def _setup_order(self, db, delivery_logs):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'deliveryLogs': delivery_logs,
            'items': '土雞蛋 x10'
        }
        db.collection.return_value.document.return_value.get.return_value = mock_doc

    def test_success(self):
        db = make_mock_db()
        self._setup_order(db, [
            {'stamp': '2026-03-18 10:00:00', 'delivery_date': '2026-03-18', 'qty': 5, 'address': '新竹市'}
        ])
        success, result = FirestoreService.correct_delivery_log('ORD001', 0, 3, '竹北市', '2026-03-20')
        self.assertTrue(success)
        self.assertEqual(result['new_qty'], 3)
        self.assertEqual(result['new_address'], '竹北市')

    def test_order_not_found(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, msg = FirestoreService.correct_delivery_log('ORD999', 0, 3)
        self.assertFalse(success)
        self.assertEqual(msg, '訂單不存在')

    def test_invalid_log_index(self):
        db = make_mock_db()
        self._setup_order(db, [
            {'stamp': '2026-03-18 10:00:00', 'qty': 5, 'address': '新竹市'}
        ])
        success, msg = FirestoreService.correct_delivery_log('ORD001', 99, 3)
        self.assertFalse(success)
        self.assertIn('不存在', msg)

    def test_marks_log_as_corrected(self):
        db = make_mock_db()
        self._setup_order(db, [
            {'stamp': '2026-03-18 10:00:00', 'delivery_date': '2026-03-18', 'qty': 5, 'address': '新竹市'}
        ])
        success, result = FirestoreService.correct_delivery_log('ORD001', 0, 3, '竹北市')
        self.assertTrue(success)
        # 確認 corrected_qty 被記錄
        update_call = db.collection.return_value.document.return_value.update.call_args
        updated_logs = update_call[0][0]['deliveryLogs']
        self.assertTrue(updated_logs[0]['is_corrected'])
        self.assertEqual(updated_logs[0]['corrected_qty'], 3)


class TestUpdateOrderStatus(unittest.TestCase):

    def test_success(self):
        db = make_mock_db()
        result = FirestoreService.update_order_status('ORD001', '已完成')
        self.assertTrue(result)
        db.collection.assert_called_with('orders')

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.update_order_status('ORD001', '已完成')
        self.assertFalse(result)


class TestUpdateOrderPaymentStatus(unittest.TestCase):

    def test_success(self):
        db = make_mock_db()
        result = FirestoreService.update_order_payment_status('ORD001', '已付款')
        self.assertTrue(result)

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        result = FirestoreService.update_order_payment_status('ORD001', '已付款')
        self.assertFalse(result)


class TestAddAuditLog(unittest.TestCase):

    def test_success(self):
        db = make_mock_db()
        mock_ref = MagicMock()
        mock_ref[1].id = 'audit_001'
        db.collection.return_value.add.return_value = mock_ref
        success, result = FirestoreService.add_audit_log(
            'ORD001', 'update_delivery', 'admin',
            {'qty': 5}, {'qty': 3}, '客戶更改'
        )
        self.assertTrue(success)
        self.assertEqual(result['orderId'], 'ORD001')

    def test_db_exception_returns_false(self):
        db = make_mock_db()
        db.collection.side_effect = Exception('DB error')
        success, msg = FirestoreService.add_audit_log(
            'ORD001', 'update_delivery', 'admin',
            {}, {}, '測試'
        )
        self.assertFalse(success)


class TestUpdateProductStock(unittest.TestCase):

    def test_success_increase_stock(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'name': '土雞蛋', 'stock': 10}
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, result = FirestoreService.update_product_stock('prod_001', 5, '進貨')
        self.assertTrue(success)
        self.assertEqual(result['oldStock'], 10)
        self.assertEqual(result['newStock'], 15)

    def test_negative_stock_rejected(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'name': '土雞蛋', 'stock': 3}
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, msg = FirestoreService.update_product_stock('prod_001', -5, '出貨')
        self.assertFalse(success)
        self.assertIn('庫存不足', msg)

    def test_product_not_found(self):
        db = make_mock_db()
        mock_doc = MagicMock()
        mock_doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = mock_doc
        success, msg = FirestoreService.update_product_stock('prod_999', 5, '進貨')
        self.assertFalse(success)
        self.assertEqual(msg, '商品不存在')


if __name__ == '__main__':
    unittest.main()
