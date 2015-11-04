# -*- coding: utf-8 -*-
import os
import csv
import datetime
import unittest2
from operator import attrgetter

import erppeek

ERPPEEK_TEST_ENV = "demo"
MODULE_NAME = "ecommerce_webservice"
SHOP_ID = "cafebabe"

def get_expected_values(record, fields):
    expected_values = []
    for rv in attrgetter(*fields)(record):
        if isinstance(rv, erppeek.Record):
            expected_values.append(rv.id)
        elif isinstance(rv, erppeek.RecordList):
            expected_values.append([el.id for el in rv])
        else:
            expected_values.append(rv)
    return dict(zip(fields, expected_values))


class SomeTest(unittest2.TestCase):

    def setUp(self):
        self.admin = erppeek.Client.from_config(ERPPEEK_TEST_ENV)
        tax_ids = self.admin.model('account.tax').search([])
        my_tax = tax_ids[0]
        self.admin.model('account.tax').browse(my_tax).api_code = 'my_tax'
        self.product = self.admin.model('product.product').create({
            'name': "BlueBeery",
            'sale_ok' : True,
            'type': 'product',
            'list_price': 3.0,
            'procure_method': 'make_to_stock',
            'taxes_id': [my_tax],
            })

        # def test00_create_external_user_and_shop(self):
        self.load_csv('demo/res.partner.csv')
        self.load_csv('demo/res.users.csv')
        self.load_csv('demo/ecommerce.api.shop.csv')

        # def test01_login_as_external_user(self):
        self.public = erppeek.Client(self.admin._server, self.admin._db,
                'ecommerce_demo_external_user', 'dragon')
        self.api = self.public.model('ecommerce.api.v1')

    def tearDown(self):
        tax_ids = self.admin.model('account.tax').search([('api_code', '=', 'my_tax')])
        if tax_ids:
            my_tax = tax_ids[0]
            self.admin.model('account.tax').browse(my_tax).api_code = False

    def load_csv(self, filename):
        modelname = os.path.splitext(os.path.basename(filename))[0]
        records = csv.reader(open(filename, 'rb'))
        fieldnames = records.next()
        rows = [values for values in list(records) if values]
        return self.admin.model(modelname).load(fieldnames, rows)

    def test02_create_customer(self):
        values = {
                'name': 'Test created customer',
                'active': True,
                'street': 'of Philadelphia',
                'street2': 'empty',
                'city': 'Sin',
                'zip': '1040',
                'country': 'CH',
                'phone': '555-123456',
                'mobile': '555-987654',
                'fax': 'no fax',
                'email': 'john.smith@example.com',
                }
        customer_id = self.api.create_customer(SHOP_ID, values)
        customer = self.admin.model('res.partner').browse(customer_id)
        self.assertEqual(customer.country_id.code.upper(), 'CH')
        values.pop('country')
        fields = values.keys()
        expected_values = attrgetter(*fields)(customer)
        self.assertSequenceEqual(expected_values, values.values())

    def test03_update_customer(self):
        values = {
                'name': 'Test another created customer',
                'country': 'CH',
                }
        customer_id = self.api.create_customer(SHOP_ID, values)
        values = {
                'name': 'Test created then updated customer',
                'country': 'FR',
                }
        self.api.update_customer(SHOP_ID, customer_id, values)
        customer = self.admin.model('res.partner').browse(customer_id)
        self.assertEqual(customer.country_id.code.upper(), 'FR')

    def test04_create_customer_address(self):
        pids = self.admin.model('res.partner').search([('type', '=', 'default')])
        partner_id = max(pids)
        values = {
                'name': 'Test created customer address',
                'active': True,
                'street': 'spirit',
                'street2': 'empty',
                'city': 'Sim',
                'zip': '1020',
                'country': 'BE',
                'type': 'invoice',
                'phone': '555-111111',
                'mobile': '555-111112',
                'fax': 'who uses fax?',
                'email': 'scott.tiger@example.com',
                }
        address_id = self.api.create_customer_address(SHOP_ID, partner_id, values)
        address = self.admin.model('res.partner').browse(address_id)
        self.assertEqual(address.country_id.code.upper(), 'BE')
        values.pop('country')
        self.assertEqual(address.parent_id.id, partner_id)
        fields = values.keys()
        expected_values = attrgetter(*fields)(address)
        self.assertSequenceEqual(expected_values, values.values())

    def test05_update_customer(self):
        values = {
                'name': 'Test another created customer address',
                'country': 'CH',
                }
        address_id = self.api.create_customer_address(SHOP_ID, None, values)
        values = {
                'name': 'Test created then updated customer address',
                'country': 'BE',
                }
        self.api.update_customer_address(SHOP_ID, address_id, values)
        customer = self.admin.model('res.partner').browse(address_id)
        self.assertEqual(customer.country_id.code.upper(), 'BE')

    def test06_create_sale_order(self):
        pids = self.admin.model('res.partner').search([('type', '=', 'default')])
        partner_id = max(pids)
        order_line = [{
            'product_id': self.product.id,
            'name': 'some description',
            'price_unit': 3.14,
            'discount': .5,
            'product_uom_qty': 10.0,
            'sequence': 0,
            'tax_id': ['my_tax'],
            }, {
            'product_id': self.product.id,
            'name': 'some description',
            'price_unit': 3.14,
            'discount': .5,
            'product_uom_qty': 10.0,
            'sequence': 1,
            # no tax defined but must take the same as it's defined on product
            }]
        now =  datetime.datetime.now()
        values = {
                'name': 'Test created sale order %s' % now,
                'client_order_ref': 'COR-622',
                'date_order': now.strftime('%Y-%m-%d'),
                'note': 'some note',
                'origin': 'some origin',
                'partner_id': partner_id,
                'partner_invoice_id': partner_id,
                'partner_shipping_id': partner_id,
                'order_line': order_line,
                }
        so_id = self.api.create_sale_order(SHOP_ID, values)
        so = self.admin.model('sale.order').browse(so_id)
        for i, sol in enumerate(so.order_line):
            sol_fields = order_line[i].keys()
            expected_values = get_expected_values(sol, sol_fields)
            if 'tax_id' in order_line[i]:
                tax_codes = self.admin.model('account.tax').browse(sol.tax_id.id).api_code
                expected_values['tax_id'] = tax_codes
            self.assertEqual(expected_values, order_line[i])
        values.pop('order_line')
        fields = values.keys()
        expected_values = get_expected_values(so, fields)
        self.assertEqual(expected_values, values)

    def test07_search_read_product_template(self):
        # TODO: enhance test
        products = self.api.search_read_product_template(SHOP_ID,
                [('name', '=', 'BlueBeery'), ('id', '=', self.product.id)])
        self.assertIn(self.product.id, [p['id'] for p in products])

    def test08_get_inventory(self):
        # TODO: enhance test
        inventory = self.api.get_inventory(SHOP_ID, [self.product.id])
        for row in inventory:
            self.assertEqual(row['id'], self.product.id)
            self.assertIsInstance(row['qty_available'], float)
            self.assertIsInstance(row['virtual_available'], float)

    def test09_get_transfer_status(self):
        # TODO: enhance test
        status = self.api.get_transfer_status(SHOP_ID, [])
        for s in status:
            self.assertRegexpMatches(s['name'], "OUT/\d{5}")

    def test10_get_payment_status(self):
        # TODO: enhance test
        fields = ['id', 'state', 'sale_order_ids']
        result = self.api.get_payment_status(SHOP_ID, [], fields)
        for row in result:
            self.assertItemsEqual(fields, row.keys())

    def test11_check_customer_credit(self):
        # TODO: enhance test
        pids = self.admin.model('res.partner').search([('type', '=', 'default')])
        partner_id = max(pids)
        result = self.api.check_customer_credit(SHOP_ID, [partner_id])
        for row in result:
            self.assertEqual(row['id'], partner_id)
            self.assertIsInstance(row['credit'], (int, float))

    def test12_get_docs(self):
        # TODO: enhance poor test
        pdfmagic = "%PDF"
        result = self.api.get_docs(SHOP_ID, 5, 'sale.order')
        self.assertEqual(result.decode('base64')[0:4], pdfmagic)
        result = self.api.get_docs(SHOP_ID, 5, 'stock.picking')
        self.assertEqual(result.decode('base64')[0:4], pdfmagic)
        result = self.api.get_docs(SHOP_ID, 1, 'account.invoice')
        self.assertEqual(result.decode('base64')[0:4], pdfmagic)

    def test13_flat_domains(self):
        customers = self.api.search_read_customer(SHOP_ID, ['customer=True'],
                ['name', 'customer'])
        if customers:
            self.assertEqual(customers[0]['customer'], True)

    def test14_eager_loading(self):
        products = self.api.search_read_product_variant(SHOP_ID,
                [('name', '=', 'BlueBeery'), ('id', '=', self.product.id)])
        self.assertIsInstance(products[0]['categ_id'], dict)
        self.assertItemsEqual(products[0]['categ_id'].keys(), ['id', 'name', 'type'])

if __name__ == '__main__':
    unittest2.main()

