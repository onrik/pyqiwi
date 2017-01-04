# coding: utf-8
from datetime import datetime
from decimal import Decimal
from unittest import TestCase

import httpretty

from pyqiwi import QiwiError, Qiwi


class QiwiErrorTestCase(TestCase):
    def test_error_code(self):
        error = QiwiError(143)
        self.assertEqual(error.code, 143)


@httpretty.activate
class QiwiClientTestCase(TestCase):
    shop_id = '123'
    api_id = '456'
    api_password = '123qwe'
    notification_password = 'qwe123'

    def setUp(self):
        self.client = Qiwi(self.shop_id, self.api_id, self.api_password, self.notification_password)

    def tearDown(self):
        httpretty.reset()

    def test__get_invoice_url(self):
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
            b'Basic dXNlcjE6cGFzc3dvcmQ='
        )

        self.assertEqual(
            self.client._make_auth('123456', 'zLQkZDdRvBNUkf9spassword'),
            b'Basic MTIzNDU2OnpMUWtaRGRSdkJOVWtmOXNwYXNzd29yZA=='
        )

    def test__make_signature(self):
        signature = self.client._make_signature({
            'b': 'bar',
            'a': 'foo',
            'some': 'param',
            'comment': u'Заказ №101'
        })

        self.assertEqual(signature, b'7nHZIf/w6DLq+CuvzV2BmhT71xA=')

    def test__request(self):
        url = 'http://example.com'
        auth = self.client._make_auth(self.api_id, self.api_password).decode('utf-8')

        httpretty.register_uri(httpretty.GET, url, '{"response": {"result_code": 0}}')

        response = self.client._request(url)
        request = httpretty.HTTPretty.last_request
        self.assertEqual(response, {'result_code': 0})
        self.assertEqual(request.headers.get('Accept'), 'application/json')
        self.assertEqual(request.headers.get('Authorization'), auth)

        httpretty.register_uri(httpretty.PUT, url, '{"response": {"result_code": 0}}')
        response = self.client._request(url, {'user': 'tel:+79998887766'})
        request = httpretty.HTTPretty.last_request
        self.assertEqual(response, {'result_code': 0})
        self.assertEqual(request.headers.get('Accept'), 'application/json')
        self.assertEqual(request.headers.get('Authorization'), auth)
        self.assertEqual(request.headers.get('Content-Type'), 'application/x-www-form-urlencoded')
        self.assertEqual(request.body, b'user=tel%3A%2B79998887766')

        httpretty.reset()
        httpretty.register_uri(
            httpretty.GET, url, '{"response": {"result_code": 33}}', status=400)
        try:
            self.client._request(url)
        except QiwiError as e:
            self.assertEqual(e.code, 33)
        else:
            self.fail('QiwiError not raised')

    def test_create_invoice(self):
        invoice_id = '101'
        url = self.client._get_invoice_url(invoice_id)
        httpretty.register_uri(httpretty.PUT, url, body="""{
            "response": {
                "result_code": 0,
                "bill": {
                    "invoice_id": "101"
                }
            }
        }""")

        invoice = self.client.create_invoice(
            invoice_id=invoice_id,
            amount=Decimal('22.00'),
            currency='RUB',
            comment='Order #101',
            user='tel:+79998887766',
            lifetime=datetime(2017, 1, 2, 15, 22, 33),
        )

        self.assertEqual(invoice, {'invoice_id': '101'})
        self.assertEqual(httpretty.HTTPretty.last_request.parsed_body, {
            'amount': ['22.00'],
            'ccy': ['RUB'],
            'comment': ['Order #101'],
            'user': ['tel: 79998887766'],
            'lifetime': ['2017-01-02T15:22:33']
        })

    def test_cancel_invoice(self):
        invoice_id = '102'
        url = self.client._get_invoice_url(invoice_id)
        httpretty.register_uri(httpretty.PATCH, url, body="""{
            "response": {
                "result_code": 0,
                "bill": {
                    "invoice_id": "102",
                    "status": "rejected"
                }
            }
        }""")

        invoice = self.client.cancel_invoice(invoice_id)

        self.assertEqual(invoice, {
            'invoice_id': '102',
            'status': "rejected",
        })

        self.assertEqual(
            httpretty.HTTPretty.last_request.body,
            b'status=rejected'
        )

    def test_get_invoice(self):
        invoice_id = '103'
        url = self.client._get_invoice_url(invoice_id)

        httpretty.register_uri(httpretty.GET, url, body="""{
            "response": {
                "result_code": 0,
                "bill": {
                    "invoice_id": "103",
                    "status": "paid"
                }
            }
        }""")

        invoice = self.client.get_invoice(invoice_id)

        self.assertEqual(invoice, {
            'invoice_id': '103',
            'status': "paid",
        })

    def test_create_refund(self):
        invoice_id = '104'
        refund_id = '1'
        url = self.client._get_refund_url(invoice_id, refund_id)

        httpretty.register_uri(httpretty.PUT, url, body="""{
           "response": {
               "result_code": 0,
               "refund": {
                   "invoice_id": "104",
                   "refund_id": "1",
                   "amount": "100.00"
               }
           }
       }""")

        refund = self.client.create_refund(invoice_id, refund_id, Decimal('100.00'))

        self.assertEqual(refund, {
            'invoice_id': '104',
            'refund_id': '1',
            'amount': '100.00',
        })

        self.assertEqual(
            httpretty.HTTPretty.last_request.body,
            b'amount=100.00'
        )

    def test_get_refund(self):
        invoice_id = '105'
        refund_id = '1'
        url = self.client._get_refund_url(invoice_id, refund_id)

        httpretty.register_uri(httpretty.GET, url, body="""{
           "response": {
               "result_code": 0,
               "refund": {
                   "invoice_id": "104",
                   "refund_id": "1",
                   "amount": "100.00",
                   "status": "fail"
               }
           }
        }""")

        refund = self.client.get_refund(invoice_id, refund_id)

        self.assertEqual(refund, {
            'invoice_id': '104',
            'refund_id': '1',
            'amount': '100.00',
            'status': 'fail',
        })

    def test_get_invoice_url(self):
        url = self.client.get_invoice_url('106')
        expected = 'https://bill.qiwi.com/order/external/main.action?' + self.client._urlencode({
            'shop': self.client.shop_id,
            'transaction': '106',
        })
        self.assertEqual(url, expected)

        url = self.client.get_invoice_url('107', True, 'http://google.com/success', 'http://google.com/fail', 'iframe', 'qw')
        expected = 'https://bill.qiwi.com/order/external/main.action?' + self.client._urlencode({
            'shop': self.client.shop_id,
            'transaction': '107',
            'iframe': True,
            'success_url': 'http://google.com/success',
            'fail_url': 'http://google.com/fail',
            'target': 'iframe',
            'pay_source': 'qw',
        })
        self.assertEqual(url, expected)

    def test_check_auth(self):
        self.assertFalse(self.client.check_auth(''))
        self.assertFalse(self.client.check_auth(None))
        self.assertFalse(self.client.check_auth(b'Basic MTExOjIyMg=='))
        self.assertTrue(self.client.check_auth(b'Basic MTIzOnF3ZTEyMw=='))

    def test_check_signature(self):
        self.assertFalse(self.client.check_signature('', {}))
        self.assertFalse(self.client.check_signature('', {'foo': 'bar'}))
        self.assertFalse(self.client.check_signature(b'W18ltrPJoSb2N7AEM5Iik02wE10=', {'foo': '111'}))
        self.assertTrue(self.client.check_signature(b'4C8pyw0rweDE0gZDYWT3E1B92aQ=', {
            'foo': 'bar',
            'commend': u'Заказ №102',
        }))
