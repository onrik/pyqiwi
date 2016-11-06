# coding: utf-8
import json
import hmac
import base64
import urllib
import hashlib
import urllib2


class QiwiError(Exception):
    def __init__(self, code, description=''):
        super(QiwiError, self).__init__(
            'Result code: %s (%s)' % (code, description))
        self.code = code


class Qiwi(object):
    REDIRECT_URL = 'https://bill.qiwi.com/order/external/main.action'
    INVOICE_URL = 'https://api.qiwi.com/api/v2/prv/{prv_id}/bills/{bill_id}'
    REFUND_URL = INVOICE_URL + '/refund/{refund_id}'

    INVOICE_STATUS_WAITING = 'waiting'
    INVOICE_STATUS_PAID = 'paid'
    INVOICE_STATUS_UNPAID = 'unpaid'
    INVOICE_STATUS_REJECTED = 'rejected'
    INVOICE_STATUS_EXPIRED = 'expired'

    REFUND_STATUS_PROCESSING = 'processing'
    REFUND_STATUS_SUCCESS = 'success'
    REFUND_STATUS_FAIL = 'fail'

    def __init__(self, shop_id, api_id, api_password, notification_password):
        # type: (str, str, str, str)
        """
        :param shop_id: Merchant id
        :param api_id: Merchant app id
        :param api_password: Merchant app password
        :param notification_password: Notification password
        """
        self.shop_id = shop_id
        self.api_id = api_id
        self.api_password = api_password
        self.notification_password = notification_password

    def _get_invoice_url(self, invoice_id):
        # type: (str) -> str
        return self.INVOICE_URL.format(prv_id=self.shop_id, bill_id=invoice_id)

    def _get_refund_url(self, invoice_id, refund_id):
        # type: (str, str) -> str
        return self.REFUND_URL.format(prv_id=self.shop_id, bill_id=invoice_id,
                                      refund_id=refund_id)

    def _urlencode(self, params):
        # type: (dict) -> str
        return urllib.urlencode({k: v for k, v in params.items() if v})

    def _make_auth(self, username, password):
        # type: (str, str) -> str
        return 'Basic %s' % base64.b64encode('%s:%s' % (username, password))

    def _make_signature(self, data):
        # type: (dict) -> str
        joined = u'|'.join(data[key] for key in sorted(data.keys()))
        return base64.b64encode(hmac.new(
            self.notification_password, joined.encode('utf-8'), hashlib.sha1
        ).digest())

    def _request(self, url, data=None, method='GET'):
        # type: (str, dict, str) -> dict
        request = urllib2.Request(url, headers={
            'Accept': 'application/json',
            'Authorization': self._make_auth(self.api_id, self.api_password),
        })
        if data:
            request.add_data(self._urlencode(data))
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            request.get_method = lambda: method

        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            response = e

        response = json.load(response)['response']
        if response['result_code'] > 0:
            raise QiwiError(response['result_code'], response.get('description', ''))
        else:
            return response

    def create_invoice(self, invoice_id, amount, currency, comment, user, lifetime, pay_source='', prv_name=''):
        # type: (str, decimal.Decimal, str, str, str, datetime.datetime, str, str) -> dict
        """
        Create invoice
        :param invoice_id: Merchant invoice id
        :param amount: Invoice amount
        :param currency: Currency (Alpha-3 ISO 4217 code)
        :param comment: Invoice comment
        :param user: String of the form "tel:<phone_number>",
        :param lifetime: Invoice expiration datetime (ISO 8601 format) in Europe/Moscow timezone
        :param pay_source: Payment source ("mobile" or "qw")
        :param prv_name: Merchant’s name.
        :return: Invoice info
        """
        params = {
            'amount': amount,
            'ccy': currency,
            'comment': comment,
            'user': user,
            'lifetime': lifetime.isoformat(),
            'pay_source': pay_source,
            'prv_name': prv_name,
        }
        response = self._request(self._get_invoice_url(invoice_id), params, 'PUT')

        return response['bill']

    def cancel_invoice(self, invoice_id):
        # type: (str) -> dict
        """
        Cancel invoice
        :param invoice_id: Merchant invoice id
        :return: Invoice info
        """
        response = self._request(
            self._get_invoice_url(invoice_id), {'status': 'rejected'}, 'PATCH')

        return response['bill']

    def get_invoice(self, invoice_id):
        # type: (str) -> dict
        """
        Get invoice info
        :param invoice_id: Merchant invoice id
        :return: Invoice info
        """
        response = self._request(self._get_invoice_url(invoice_id))

        return response['bill']

    def create_refund(self, invoice_id, refund_id, amount):
        # type: (str, str, decimal.Decimal) -> dict
        """
        Create refund
        :param invoice_id: Merchant invoice id
        :param refund_id: Merchant refund id
        :param amount: Refund amount
        :return: Refund info
        """
        url = self._get_refund_url(invoice_id, refund_id)
        response = self._request(url, {'amount': amount}, 'PUT')

        return response['refund']

    def get_refund(self, invoice_id, refund_id):
        # type: (str, str) -> dict
        """
        Get refund info
        :param invoice_id: Merchant invoice id
        :param refund_id: Merchant refund id
        :return: Refund info
        """
        response = self._request(self._get_refund_url(invoice_id, refund_id))

        return response['refund']

    def get_invoice_url(self, invoice_id, iframe=False, success_url='',
                        fail_url='', target='', pay_source=''):
        # type: (str, bool, str, str, str, str) -> str
        """
        Return URL to invoice payment page
        :param invoice_id: Merchant invoice id
        :param iframe: Invoice page would be opened in iframe
        :param success_url: The URL to which the payer will be redirected in case of successful
        :param fail_url: The URL to which the payer will be redirected when creation
        :param target: "iframe" or empty
        :param pay_source: Payment source ("mobile", "qw", "card", "wm", "ssk")
        :return: URL for redirect
        """
        return self.REDIRECT_URL + '?' + self._urlencode({
            'shop': self.shop_id,
            'transaction': invoice_id,
            'iframe': iframe,
            'success_url': success_url,
            'fail_url': fail_url,
            'target': target,
            'pay_source': pay_source,
        })

    def check_auth(self, auth):
        # type: (str) -> bool
        """
        Check that notification auth is valid
        :param auth: HTTP Authorization header value
        :return:
        """
        return self._make_auth(self.shop_id, self.notification_password) == auth

    def check_signature(self, signature, data):
        # type: (str, dict) -> bool
        """
        Check that notification data signature is valid
        :param signature: HTTP Authorization header value
        :param data: HTTP post data dict
        :return:
        """
        return self._make_signature(data) == signature
