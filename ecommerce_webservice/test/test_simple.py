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
    return expected_values


class SomeTest(unittest2.TestCase):

    def setUp(self):
        self.admin = erppeek.Client.from_config(ERPPEEK_TEST_ENV)

        # def test00_create_external_user_and_shop(self):
        self.load_csv('demo/res.partner.csv')
        self.load_csv('demo/res.users.csv')
        self.load_csv('demo/ecommerce.api.shop.csv')

        # def test01_login_as_external_user(self):
        self.public = erppeek.Client(self.admin._server, self.admin._db,
                'ecommerce_demo_external_user', 'dragon')
        self.assertEqual(self.public.user, 'ecommerce_demo_external_user')
        self.api = self.public.model('ecommerce.api.v1')

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
            'product_id': 1,
            'name': 'some description',
            'price_unit': 3.14,
            'discount': 5.0,
            'product_uom_qty': 10.0,
            'sequence': 0,
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
        sol_fields = order_line[0].keys()
        for i, sol in enumerate(so.order_line):
            expected_values = get_expected_values(sol, sol_fields)
            self.assertSequenceEqual(expected_values, order_line[i].values())
        values.pop('order_line')
        fields = values.keys()
        expected_values = get_expected_values(so, fields)
        self.assertSequenceEqual(expected_values, values.values())

    def test07_search_read_product_template(self):
        # TODO: enhance poor test
        products = self.api.search_read_product_template(SHOP_ID, [('name', '=', 'Service')])
        self.assertEqual(products[0]['id'], 1)

    def test08_get_inventory(self):
        # TODO: enhance poor test
        inventory = self.api.get_inventory(SHOP_ID, [1])
        print inventory

    def test09_get_transfer_status(self):
        # TODO: enhance poor test
        status = self.api.get_transfer_status(SHOP_ID, [])
        print status

    def test10_get_payment_status(self):
        # TODO: enhance poor test
        status = self.api.get_payment_status(SHOP_ID, [])
        print status

    def test11_check_customer_credit(self):
        # TODO: enhance poor test
        result = self.api.check_customer_credit(SHOP_ID, [ 5, 3, 6, 17, 11, 13,
            16, 18, 7, 8, 67, 4, 72, 73, 10, 9, 25, 15, 12, 19, 21, 23, 20, 66,
            14, 22, 27, 26, 1, 70, 68])
        print result

    def test12_get_docs(self):
        # TODO: enhance poor test
        pdfmagic = "%PDF"
        result = self.api.get_docs(SHOP_ID, 5, 'sale.order')
        self.assertEqual(result.decode('base64')[0:4], pdfmagic)
        result = self.api.get_docs(SHOP_ID, 5, 'stock.picking')
        self.assertEqual(result.decode('base64')[0:4], pdfmagic)
        result = self.api.get_docs(SHOP_ID, 1, 'account.invoice')
        self.assertEqual(result.decode('base64')[0:4], pdfmagic)

if __name__ == '__main__':
    unittest2.main()

