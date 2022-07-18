from urllib.parse import urlencode
import urllib.request, urllib.error, urllib.parse
from json import dumps as json_dumps
from datetime import datetime

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

    def add_product_to_user_cart(self):
        product = self.env['product.product'].search([])[0]
        self.post('/shop/cart/update', data={"product_id": product.id})

    def pay_cart(self, **params):
        """ Simulate a clik on Slimpay "Pay" button.
        `SlimpayClient.approval_url` mock returns the transaction
        reference instead of a Slimpay URL, so we can use it later to
        check the transaction.
        """
        return self.jsonrpc(
            '/payment/slimpay_transaction/%s' % self.slimpay.id, params=params)

    def simulate_feedback(self, tx_ref, state='closed.completed'):
        """ Simulate a (by default OK) Slimpay feedback.
        Requires mocks for SlimpayClient.get and SlimpayClient.get_from_doc.
        """
        feedback = {'reference': tx_ref,
                    '_links': {'self': {'href': 'http://slimpay_order_url'}}}
        self.fake_get.return_value = {
            'reference': tx_ref, 'state': state, 'id': 'test-id',
            'dateClosed': datetime.today().isoformat()}
        self.post('/payment/slimpay/s2s/feedback', data=json_dumps(feedback),
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
        self.assertEqual(1, len(tx['sale_order_ids']))
        self.check_so(tx['sale_order_ids'][0], 'sale')

    def test_slimpay_portal_sale_ok_with_token(self):
        ref = self.env.ref
        partner = ref("base.partner_demo_portal")
        acquirer = ref("account_payment_slimpay.payment_acquirer_slimpay")

        token = self.env["payment.token"].create({
            "name": "Test token",
            "partner_id": partner.id,
            "acquirer_id": acquirer.id,
            "acquirer_ref": "test slimpay ref",
        })

        self.authenticate('portal', 'portal')
        self.add_product_to_user_cart()

        def action_mock(action, short_method_name, *args, **kwargs):
            return {
                ("GET", "get-mandates"): {"reference": "test mandate ref"},
                ("POST", "create-payins"): {
                    "executionStatus": "toprocess",
                    "state": "accepted",
                    "reference": "payment reference",
                },
            }[(action, short_method_name)]

        with patch.object(
                SlimpayClient, 'action', side_effect=action_mock) as mocked_act:
            result = self.pay_cart(token=token.id)

        self.assertEqual(result, "/shop/payment/validate")
        calls = mocked_act.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], ("GET", "get-mandates"))
        self.assertEqual(calls[1][0], ("POST", "create-payins"))

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
        self.assertFalse(tx1['sale_order_ids'])

        tx2_ref = self.pay_cart()
        self.check_transaction(tx2_ref, 'draft')
        self.simulate_feedback(tx2_ref)
        tx2 = self.check_transaction(tx2_ref, 'done')
        self.assertEqual(1, len(tx2['sale_order_ids']))
        self.check_so(tx2['sale_order_ids'][0], 'sale')
        # Check transactions' reference start with the same SO name
        self.assertEqual(1, len(set(tx['reference'].split('-')[0]
                                    for tx in (tx1, tx2))))
