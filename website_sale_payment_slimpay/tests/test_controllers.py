from urllib import urlencode
import urllib2
import json
from datetime import datetime

from mock import patch

from odoo.addons.payment_slimpay.models.payment import SlimpayClient

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
            patch('odoo.addons.payment_slimpay.models.'
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
        self.slimpay = self.env.ref('payment.payment_acquirer_slimpay')

    def _start_patcher(self, patcher):
        self._patchers.append(patcher)
        return patcher.start()

    def post(self, path, data=None, encoder=urlencode,
             headers=None, timeout=30, assert_code=200):
        """ POST an http request using an urllib2 Request object.
        Complements HttpCase.url_open with POST and bigger default timeout """
        data = encoder(data or {})
        url = 'http://%s:%s%s' % (HOST, PORT, path)
        req = urllib2.Request(url, data, headers or {})
        resp = self.opener.open(req, data, timeout)
        self.assertEqual(assert_code, resp.code)
        return resp.read()

    def jsonrpc(self, path, params=None, timeout=30, assert_code=200):
        " Helper method to perform a jsonrpc request and return its result "
        headers = {'Content-Type': 'application/json'}
        data = {"jsonrpc": "2.0", "method": "call", "params": params or {}}
        return json.loads(self.post(
            path, data, json.dumps, headers, timeout, assert_code))['result']

    def search_read(self, model, domain, kwargs=None):
        " Helper method to perform a model + domain search via jsonrpc "
        return self.jsonrpc('/web/dataset/call_kw', {
            'model': model, 'method': 'search_read', 'args': [domain],
            'kwargs': kwargs or {}})

    def add_product_to_user_cart(self):
        product = self.env['product.product'].search([])[0]
        self.post('/shop/cart/update', {"product_id": product.id})

    def pay_cart(self):
        """ Simulate a clik on Slimpay "Pay" button.
        `SlimpayClient.approval_url` mock returns the transaction
        reference instead of a Slimpay URL, so we can use it later to
        check the transaction.
        """
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
        self.post('/payment/slimpay/s2s/feedback', feedback, json.dumps,
                  {'Content-Type': 'application/hal+json'})

    def check_transaction(self, tx_ref, state):
        tx = self.search_read('payment.transaction',
                              [('reference', '=', tx_ref)])[0]
        self.assertEqual(state, tx['state'])
        self.assertEqual([self.slimpay.id, self.slimpay.name],
                         tx['acquirer_id'])
        return tx

    def test_slimpay_portal_sale_ok(self):
        """ Perform a portal sale, paid using a mocked Slimpay and using a fake
        feedback.
        """
        # A portal user adds a product in its cart and clicks the "Buy" button
        self.authenticate('portal', 'portal')
        self.add_product_to_user_cart()
        tx_ref = self.pay_cart()

        self.check_transaction(tx_ref, 'draft')
        self.simulate_feedback(tx_ref)
        tx = self.check_transaction(tx_ref, 'done')

        self.assertEqual('IBAN my-iban (my-bank)', tx['payment_token_id'][1])
        self.assertEqual('sale', tx['so_state'])

    def test_slimpay_portal_sale_ok_with_two_transaction(self):
        """ Perform a successful portal sale in two steps:
        - first transaction fails (typically times out while user finds its
        bank coordinates)
        - second transaction succeeds.
        """
        self.authenticate('portal', 'portal')
        self.add_product_to_user_cart()

        tx1_ref = self.pay_cart()
        self.check_transaction(tx1_ref, 'draft')
        self.simulate_feedback(tx1_ref, 'closed.aborted.aborted_byclient')
        tx1 = self.check_transaction(tx1_ref, 'cancel')
        self.assertEqual('draft', tx1['so_state'])

        tx2_ref = self.pay_cart()
        self.check_transaction(tx2_ref, 'draft')
        self.simulate_feedback(tx2_ref)
        tx2 = self.check_transaction(tx2_ref, 'done')
        self.assertEqual('sale', tx2['so_state'])
        self.assertEqual(tx1['sale_order_id'][0], tx2['sale_order_id'][0])
