from json import dumps as json_dumps
from datetime import datetime

import lxml.html
from mock import patch

from odoo.addons.account_payment_slimpay.models.payment import SlimpayClient

from odoo.tests.common import HttpCase, at_install, post_install, HOST, PORT


def _get_from_doc_mock(doc, method_name):
    """ Dummy mock for SimplayClient.get_from_doc that returns a hard-coded
    hal document for the requested method name, whatever the specified doc.
    """
    return {'get-mandate': {'id': 'my-mandate-id'},
            'get-bank-account': {'institutionName': 'my-bank',
                                 'iban': 'my-iban'},
            }[method_name]


@at_install(False)
@post_install(True)
class SlimpayControllersTC(HttpCase):

    def setUp(self):
        self._patchers = []
        # Mock SlimpayClient
        self._start_patcher(
            patch('odoo.addons.account_payment_slimpay.models.'
                  'slimpay_utils.get_client'))
        # Mock its "get" and "get_from_doc" methods (to ease their config)
        self.fake_get = self._start_patcher(patch.object(SlimpayClient, 'get'))
        self._start_patcher(patch.object(
            SlimpayClient, 'get_from_doc', side_effect=_get_from_doc_mock))
        # Mock approval_url
        self._start_patcher(patch.object(
            SlimpayClient, 'approval_url',
            side_effect=lambda tx_ref, *args, **kw: tx_ref))
        super(SlimpayControllersTC, self).setUp()
        # Stop patchers in case of a test exception or normal termination
        for patcher in self._patchers:
            self.addCleanup(patcher.stop)
        # Setup a journal for Slimpay acquirer
        self.slimpay = self.env.ref(
            'account_payment_slimpay.payment_acquirer_slimpay')
        journal = self.env['account.journal'].search([('type', '=', 'bank')],
                                                     limit=1).exists()
        self.slimpay.journal_id = journal.id

    def _start_patcher(self, patcher):
        self._patchers.append(patcher)
        return patcher.start()

    def post(self, path, data=None, json=None,
             headers=None, timeout=30, assert_code=200):
        """ POST an http request using requests. Complements HttpCase.url_open
        with headers, json and bigger default timeout """
        url = 'http://%s:%s%s' % (HOST, PORT, path)
        resp = self.opener.post(url, data=data, json=json, timeout=timeout,
                                headers=headers)
        self.assertEqual(assert_code, resp.status_code)
        return resp.text if json is None else resp.json()

    def jsonrpc(self, path, params=None, timeout=30, assert_code=200):
        " Helper method to perform a jsonrpc request and return its result "
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "2.0", "method": "call", "params": params or {}}
        json = self.post(
            path, json=data, headers=headers, timeout=timeout,
            assert_code=assert_code)
        try:
            return json['result']
        except KeyError:
            self.fail('jsonrpc error:\n%s' % json)

    def search_read(self, model, *args, kwargs=None):
        " Helper method to perform a model + domain search via jsonrpc "
        return self.jsonrpc('/web/dataset/call_kw', {
            'model': model, 'method': 'search_read', 'args': args,
            'kwargs': kwargs or {}})

    def csrf_token(self, html_text):
        doc = lxml.html.fromstring(html_text)
        return doc.xpath("//input[@name='csrf_token']")[0].get("value")

    def add_product_to_user_cart(self):
        product = self.env['product.product'].search([])[0]
        self.post('/shop/cart/update', data={"product_id": product.id})
        csrf_token = self.csrf_token(self.url_open('/shop/checkout').text)
        self.post('/shop/confirm_order', data={"csrf_token": csrf_token})

    def pay_cart(self, **params):
        """ Simulate a click on Slimpay "Pay" button.
        `SlimpayClient.approval_url` mock returns the transaction
        reference instead of a Slimpay URL, so we can use it later to
        check the transaction.
        """
        self.jsonrpc(
            '/shop/payment/transaction',
            params={"acquirer_id": self.slimpay.id}
        )
        return self.jsonrpc(
            '/payment/slimpay_transaction/%s' % self.slimpay.id)

    def simulate_feedback(self, tx_ref, state='closed.completed'):
        """ Simulate a (by default OK) Slimpay feedback.
        Requires mocks for SlimpayClient.get and SlimpayClient.get_from_doc.
        """
        feedback = {'reference': tx_ref,
                    '_links': {'self': {'href': 'http://slimpay_order_url'}}}
        self.fake_get.return_value = {
            'reference': tx_ref, 'state': state, 'id': 'test-id',
            'dateClosed': datetime.today().isoformat()}
        self.post(
            '/payment/slimpay/s2s/feedback', data=json_dumps(feedback),
            headers={'Content-Type': 'application/hal+json'},
        )

    def check_transaction(self, tx_ref, state):
        tx = self.search_read('payment.transaction',
                              [('reference', '=', tx_ref)])[0]
        self.assertEqual(state, tx['state'])
        self.assertEqual([self.slimpay.id, self.slimpay.name],
                         tx['acquirer_id'])
        return tx

    def check_so(self, so_id, state):
        so = self.search_read('sale.order', [('id', '=', so_id)], ['state'])
        self.assertEqual([{'id': so_id, 'state': state}], so)
