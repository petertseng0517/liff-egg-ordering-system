"""
整合測試 - Admin Routes (routes/admin.py)
"""
import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['FLASK_ENV'] = 'testing'

from app import app


class TestAdminRoutesBase(unittest.TestCase):
    """管理員路由測試基礎類"""

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        cls.client = app.test_client()

    def login(self):
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_name'] = 'test_admin'


# ===== 存取控制 =====

class TestAdminAuth(TestAdminRoutesBase):

    def test_get_orders_unauthorized(self):
        response = self.client.get('/api/admin/orders')
        self.assertEqual(response.status_code, 401)

    def test_update_status_unauthorized(self):
        response = self.client.post('/api/admin/order/update_status', json={})
        self.assertEqual(response.status_code, 401)

    def test_get_members_unauthorized(self):
        response = self.client.get('/api/admin/members')
        self.assertEqual(response.status_code, 401)

    def test_add_delivery_unauthorized(self):
        response = self.client.post('/api/admin/order/add_delivery', json={})
        self.assertEqual(response.status_code, 401)

    def test_delivery_report_unauthorized(self):
        response = self.client.get('/api/admin/reports/delivery-records')
        self.assertEqual(response.status_code, 401)


# ===== 取得所有訂單 =====

class TestGetAllOrders(TestAdminRoutesBase):

    @patch('services.database_adapter.DatabaseAdapter.get_all_orders_with_members')
    def test_success(self, mock_get):
        self.login()
        mock_get.return_value = [
            {'orderId': 'ORD001', 'status': '待確認', 'customer': {'name': '王小明'}}
        ]
        response = self.client.get('/api/admin/orders')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['orderId'], 'ORD001')

    @patch('services.database_adapter.DatabaseAdapter.get_all_orders_with_members')
    def test_returns_empty_list(self, mock_get):
        self.login()
        mock_get.return_value = []
        response = self.client.get('/api/admin/orders')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    @patch('services.database_adapter.DatabaseAdapter.get_all_orders_with_members')
    def test_db_exception_returns_500(self, mock_get):
        self.login()
        mock_get.side_effect = Exception('DB error')
        response = self.client.get('/api/admin/orders')
        self.assertEqual(response.status_code, 500)


# ===== 更新訂單狀態 =====

class TestUpdateOrderStatus(TestAdminRoutesBase):

    @patch('services.line_service.LINEService.send_status_update')
    @patch('services.database_adapter.DatabaseAdapter.update_order_status')
    def test_success_with_line_notification(self, mock_update, mock_line):
        self.login()
        mock_update.return_value = True
        response = self.client.post('/api/admin/order/update_status', json={
            'orderId': 'ORD001', 'status': '已確認', 'userId': 'U123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        mock_line.assert_called_once_with('U123', 'ORD001', '已確認')

    @patch('services.line_service.LINEService.send_status_update')
    @patch('services.database_adapter.DatabaseAdapter.update_order_status')
    def test_success_without_user_id_skips_line(self, mock_update, mock_line):
        self.login()
        mock_update.return_value = True
        response = self.client.post('/api/admin/order/update_status', json={
            'orderId': 'ORD001', 'status': '已確認'
        })
        self.assertEqual(response.status_code, 200)
        mock_line.assert_not_called()

    def test_missing_order_id(self):
        self.login()
        response = self.client.post('/api/admin/order/update_status', json={'status': '已確認'})
        self.assertEqual(response.status_code, 400)

    def test_missing_status(self):
        self.login()
        response = self.client.post('/api/admin/order/update_status', json={'orderId': 'ORD001'})
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.update_order_status')
    def test_order_not_found(self, mock_update):
        self.login()
        mock_update.return_value = False
        response = self.client.post('/api/admin/order/update_status', json={
            'orderId': 'ORD999', 'status': '已確認'
        })
        self.assertEqual(response.status_code, 404)


# ===== 更新付款狀態 =====

class TestUpdatePaymentStatus(TestAdminRoutesBase):

    @patch('services.database_adapter.DatabaseAdapter.update_order_payment_status')
    def test_success(self, mock_update):
        self.login()
        mock_update.return_value = True
        response = self.client.post('/api/admin/order/update_payment', json={
            'orderId': 'ORD001', 'paymentStatus': '已付款'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')

    def test_missing_order_id(self):
        self.login()
        response = self.client.post('/api/admin/order/update_payment', json={'paymentStatus': '已付款'})
        self.assertEqual(response.status_code, 400)

    def test_missing_payment_status(self):
        self.login()
        response = self.client.post('/api/admin/order/update_payment', json={'orderId': 'ORD001'})
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.update_order_payment_status')
    def test_order_not_found(self, mock_update):
        self.login()
        mock_update.return_value = False
        response = self.client.post('/api/admin/order/update_payment', json={
            'orderId': 'ORD999', 'paymentStatus': '已付款'
        })
        self.assertEqual(response.status_code, 404)


# ===== 新增出貨紀錄 =====

class TestAddDeliveryLog(TestAdminRoutesBase):

    @patch('services.line_service.LINEService.send_delivery_notification')
    @patch('services.database_adapter.DatabaseAdapter.add_delivery_log')
    def test_success(self, mock_add, mock_line):
        self.login()
        mock_add.return_value = (True, {
            'status': '部分配送',
            'total_delivered': 5,
            'delivery_date': '2026-03-18'
        })
        response = self.client.post('/api/admin/order/add_delivery', json={
            'orderId': 'ORD001', 'userId': 'U123',
            'qty': 5, 'address': '新竹市',
            'delivery_date': '2026-03-18', 'totalOrdered': 10
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')
        mock_line.assert_called_once()

    def test_zero_qty_rejected(self):
        self.login()
        response = self.client.post('/api/admin/order/add_delivery', json={
            'orderId': 'ORD001', 'qty': 0
        })
        self.assertEqual(response.status_code, 400)

    def test_missing_order_id_rejected(self):
        self.login()
        response = self.client.post('/api/admin/order/add_delivery', json={'qty': 5})
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.add_delivery_log')
    def test_order_not_found(self, mock_add):
        self.login()
        mock_add.return_value = (False, '訂單不存在')
        response = self.client.post('/api/admin/order/add_delivery', json={
            'orderId': 'ORD999', 'qty': 5, 'totalOrdered': 10
        })
        self.assertEqual(response.status_code, 400)


# ===== 修正出貨紀錄 =====

class TestCorrectDeliveryLog(TestAdminRoutesBase):

    @patch('services.line_service.LINEService.send_delivery_correction_notification')
    @patch('services.database_adapter.DatabaseAdapter.add_audit_log')
    @patch('services.database_adapter.DatabaseAdapter.correct_delivery_log')
    def test_success(self, mock_correct, mock_audit, mock_line):
        self.login()
        mock_correct.return_value = (True, {'status': '部分配送', 'new_qty': 3})
        mock_audit.return_value = (True, {})
        response = self.client.post('/api/admin/order/correct_delivery', json={
            'orderId': 'ORD001', 'userId': 'U123',
            'logIndex': 0, 'newQty': 3,
            'newAddress': '新竹市', 'newDeliveryDate': '2026-03-18',
            'reason': '客戶更改數量',
            'oldQty': 5, 'oldAddress': '竹北市', 'oldDeliveryDate': '2026-03-15'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')

    def test_missing_reason_rejected(self):
        self.login()
        response = self.client.post('/api/admin/order/correct_delivery', json={
            'orderId': 'ORD001', 'logIndex': 0, 'newQty': 3, 'reason': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('原因', json.loads(response.data)['msg'])

    def test_zero_qty_rejected(self):
        self.login()
        response = self.client.post('/api/admin/order/correct_delivery', json={
            'orderId': 'ORD001', 'logIndex': 0, 'newQty': 0, 'reason': '測試'
        })
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.correct_delivery_log')
    def test_delivery_log_not_found(self, mock_correct):
        self.login()
        mock_correct.return_value = (False, '出貨紀錄不存在')
        response = self.client.post('/api/admin/order/correct_delivery', json={
            'orderId': 'ORD001', 'logIndex': 99, 'newQty': 3, 'reason': '測試'
        })
        self.assertEqual(response.status_code, 400)


# ===== 店家為會員建立訂單 =====

class TestCreateOrderForMember(TestAdminRoutesBase):

    @patch('services.line_service.LINEService.send_push_message')
    @patch('services.database_adapter.DatabaseAdapter.add_order')
    @patch('services.database_adapter.DatabaseAdapter.get_product')
    @patch('services.database_adapter.DatabaseAdapter.get_member_by_id')
    def test_success(self, mock_member, mock_product, mock_add, mock_line):
        self.login()
        mock_member.return_value = (True, {'name': '王小明', 'phone': '0912345678'})
        mock_product.return_value = (True, {'price': 100, 'status': 'active', 'actualQuantity': 1})
        mock_add.return_value = True
        response = self.client.post('/api/admin/order/create-for-member', json={
            'userId': 'U123', 'productId': 'prod_001',
            'itemName': '土雞蛋', 'qty': 5
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('orderId', data)
        self.assertIn('王小明', data['msg'])

    def test_missing_params(self):
        self.login()
        response = self.client.post('/api/admin/order/create-for-member', json={'userId': 'U123'})
        self.assertEqual(response.status_code, 400)

    def test_zero_qty_rejected(self):
        self.login()
        response = self.client.post('/api/admin/order/create-for-member', json={
            'userId': 'U123', 'productId': 'prod_001', 'itemName': '土雞蛋', 'qty': 0
        })
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.get_member_by_id')
    def test_member_not_found(self, mock_member):
        self.login()
        mock_member.return_value = (False, '會員不存在')
        response = self.client.post('/api/admin/order/create-for-member', json={
            'userId': 'U999', 'productId': 'prod_001', 'itemName': '土雞蛋', 'qty': 5
        })
        self.assertEqual(response.status_code, 404)

    @patch('services.database_adapter.DatabaseAdapter.get_product')
    @patch('services.database_adapter.DatabaseAdapter.get_member_by_id')
    def test_product_not_found(self, mock_member, mock_product):
        self.login()
        mock_member.return_value = (True, {'name': '王小明'})
        mock_product.return_value = (False, '商品不存在')
        response = self.client.post('/api/admin/order/create-for-member', json={
            'userId': 'U123', 'productId': 'prod_999', 'itemName': '土雞蛋', 'qty': 5
        })
        self.assertEqual(response.status_code, 404)

    @patch('services.database_adapter.DatabaseAdapter.get_product')
    @patch('services.database_adapter.DatabaseAdapter.get_member_by_id')
    def test_inactive_product_rejected(self, mock_member, mock_product):
        self.login()
        mock_member.return_value = (True, {'name': '王小明'})
        mock_product.return_value = (True, {'price': 100, 'status': 'inactive'})
        response = self.client.post('/api/admin/order/create-for-member', json={
            'userId': 'U123', 'productId': 'prod_001', 'itemName': '土雞蛋', 'qty': 5
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('下架', json.loads(response.data)['msg'])


# ===== 會員管理 =====

class TestMemberManagement(TestAdminRoutesBase):

    @patch('services.database_adapter.DatabaseAdapter.get_all_members')
    def test_get_all_members_success(self, mock_get):
        self.login()
        mock_get.return_value = [{'userId': 'U123', 'name': '王小明'}]
        response = self.client.get('/api/admin/members')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total'], 1)

    @patch('services.database_adapter.DatabaseAdapter.get_member_by_id')
    def test_get_single_member_success(self, mock_get):
        self.login()
        mock_get.return_value = (True, {'userId': 'U123', 'name': '王小明'})
        response = self.client.get('/api/admin/member/U123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['member']['name'], '王小明')

    @patch('services.database_adapter.DatabaseAdapter.get_member_by_id')
    def test_get_single_member_not_found(self, mock_get):
        self.login()
        mock_get.return_value = (False, '會員不存在')
        response = self.client.get('/api/admin/member/U999')
        self.assertEqual(response.status_code, 404)

    @patch('services.database_adapter.DatabaseAdapter.update_member_status')
    def test_update_member_status_success(self, mock_update):
        self.login()
        mock_update.return_value = (True, '狀態更新成功')
        response = self.client.post('/api/admin/member/update_status', json={
            'userId': 'U123', 'status': '停用'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], 'success')

    def test_update_member_status_missing_params(self):
        self.login()
        response = self.client.post('/api/admin/member/update_status', json={'userId': 'U123'})
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.update_member_status')
    def test_update_member_status_invalid(self, mock_update):
        self.login()
        mock_update.return_value = (False, '無效的狀態')
        response = self.client.post('/api/admin/member/update_status', json={
            'userId': 'U123', 'status': '無效狀態'
        })
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.update_member')
    def test_update_member_info_success(self, mock_update):
        self.login()
        mock_update.return_value = True
        response = self.client.post('/api/admin/member/update', json={
            'userId': 'U123', 'name': '王大明',
            'phone': '0912345678', 'address': '新竹市'
        })
        self.assertEqual(response.status_code, 200)

    def test_update_member_info_missing_fields(self):
        self.login()
        response = self.client.post('/api/admin/member/update', json={
            'userId': 'U123', 'name': '王大明'
        })
        self.assertEqual(response.status_code, 400)


# ===== 出貨報表 =====

class TestDeliveryReport(TestAdminRoutesBase):

    @patch('services.database_adapter.DatabaseAdapter.get_all_orders_with_members')
    def test_success_with_matching_records(self, mock_get):
        self.login()
        mock_get.return_value = [{
            'orderId': 'ORD001',
            'customer': {'name': '王小明', 'phone': '0912345678'},
            'deliveryLogs': [
                {'delivery_date': '2026-03-18', 'qty': 5, 'address': '新竹市'}
            ]
        }]
        response = self.client.get('/api/admin/reports/delivery-records?delivery_date=2026-03-18')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_records'], 1)
        self.assertEqual(data['records'][0]['customer_name'], '王小明')

    @patch('services.database_adapter.DatabaseAdapter.get_all_orders_with_members')
    def test_corrected_qty_used_when_present(self, mock_get):
        self.login()
        mock_get.return_value = [{
            'orderId': 'ORD001',
            'customer': {'name': '王小明', 'phone': '0912345678'},
            'deliveryLogs': [
                {'delivery_date': '2026-03-18', 'qty': 5, 'corrected_qty': 3, 'address': '新竹市'}
            ]
        }]
        response = self.client.get('/api/admin/reports/delivery-records?delivery_date=2026-03-18')
        data = json.loads(response.data)
        self.assertEqual(data['records'][0]['delivery_qty'], 3)

    def test_missing_date_returns_400(self):
        self.login()
        response = self.client.get('/api/admin/reports/delivery-records')
        self.assertEqual(response.status_code, 400)

    def test_invalid_date_format_returns_400(self):
        self.login()
        response = self.client.get('/api/admin/reports/delivery-records?delivery_date=20260318')
        self.assertEqual(response.status_code, 400)

    @patch('services.database_adapter.DatabaseAdapter.get_all_orders_with_members')
    def test_no_matching_date_returns_empty(self, mock_get):
        self.login()
        mock_get.return_value = [{
            'orderId': 'ORD001', 'customer': {},
            'deliveryLogs': [{'delivery_date': '2026-01-01', 'qty': 5, 'address': '新竹市'}]
        }]
        response = self.client.get('/api/admin/reports/delivery-records?delivery_date=2026-03-18')
        data = json.loads(response.data)
        self.assertEqual(data['total_records'], 0)


# ===== 審計日誌 =====

class TestDeliveryAudit(TestAdminRoutesBase):

    @patch('services.database_adapter.DatabaseAdapter.get_delivery_audit_logs')
    def test_get_audit_logs_success(self, mock_get):
        self.login()
        mock_get.return_value = [
            {'orderId': 'ORD001', 'operation': 'update_delivery', 'reason': '客戶更改'}
        ]
        response = self.client.get('/api/admin/order/delivery_audit/ORD001')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)

    @patch('services.database_adapter.DatabaseAdapter.get_delivery_audit_logs')
    def test_get_audit_logs_empty(self, mock_get):
        self.login()
        mock_get.return_value = []
        response = self.client.get('/api/admin/order/delivery_audit/ORD999')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])


if __name__ == '__main__':
    unittest.main()
