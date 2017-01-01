# coding: utf-8
from unittest import TestCase

from pyqiwi import QiwiError, Qiwi


class QiwiErrorTestCase(TestCase):
    def test_error_code(self):
        error = QiwiError(143)
        self.assertEqual(error.code, 143)


class QiwiClientTestCase(TestCase):
    shop_id = '123'
    api_id = '456'
    api_password = '123qwe'
    notification_password = 'qwe123'

    def setUp(self):
        self.client = Qiwi(self.shop_id, self.api_id, self.api_password, self.notification_password)

    def test_get_invoice_url(self):
        self.assertEqual(
            self.client._get_invoice_url('10001'),
            'https://api.qiwi.com/api/v2/prv/123/bills/10001'
        )

    def test__get_refund_url(self):
        self.assertEqual(
            self.client._get_refund_url('1', '002'),
            'https://api.qiwi.com/api/v2/prv/123/bills/1/refund/002'
        )

    def test_url_encode(self):
        encoded = self.client._urlencode({
            'foo': 'bar',
            'ext': '',
            'user': 'tel:+79998887766',
        })

        self.assertEqual(encoded, 'foo=bar&user=tel%3A%2B79998887766')

    def test_make_auth(self):
        self.assertEqual(
            self.client._make_auth('user1', 'password'),
            'Basic dXNlcjE6cGFzc3dvcmQ='
        )

        self.assertEqual(
            self.client._make_auth('123456', 'zLQkZDdRvBNUkf9spassword'),
            'Basic MTIzNDU2OnpMUWtaRGRSdkJOVWtmOXNwYXNzd29yZA=='
        )

    def test__make_signature(self):
        signature = self.client._make_signature({
            'b': 'bar',
            'a': 'foo',
            'some': 'param',
        })

        self.assertEqual(signature, 'Xk3rStjrqwlLfivnlpIDdAgj5fw=')
