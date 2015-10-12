# -*- coding: utf-8 -*-
import csv
import sys
import datetime
import unittest2
from operator import attrgetter

import erppeek

ERPPEEK_TEST_ENV = "test"
MODULE_NAME = "ecommerce_webservice"
SHOP_ID = "cafebabe"

class BaseTest(unittest2.TestCase):

    def parse_csv(self, filename):
        records = csv.reader(open(filename, 'rb'))
        fieldnames = records.next()
        rows = [values for values in list(records) if values]
        return fieldnames, rows


class SomeTest(BaseTest):

    def setUp(self):
        # init erppeek client
        #now = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        #template_db = 'test_%s' % MODULE_NAME
        #if not client.db.db_exist(template_db):
        #    print "create db with all dependencies of current module"
        #test_db = '%s_%s' % (template_db, now)
        #if erppeek.Client.db.duplicate_database('admin', template_db, test_db):
        #    self._o = connect to test_db with external uid
        #self._o.install('ecommerce_webservice')

        # init erppeek client
        env = ERPPEEK_TEST_ENV
        self._o = erppeek.Client.from_config(env)
        sys.ps1 = "%s@%s-%s >>> " % (self._o.user, self._o._db, env)

        # cache some models
        self.shop = self._o.model('ecommerce.api.shop')
        self.api = self._o.model('ecommerce.api.v1')
        self.log = self._o.model('ecommerce.api.log')

    def test0_create_external_user(self):
        f, r = self.parse_csv('demo/res.partner.csv')
        self._o.model('res.partner').load(f, r)
        f, r = self.parse_csv('demo/res.users.csv')

    def test1_create_shop(self):
        f, r = self.parse_csv('demo/ecommerce.api.shop.csv')
        self.shop.load(f, r)

    def test2_create_customer(self):
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
        customer = self._o.model('res.partner').browse(customer_id)
        self.assertEqual(customer.country_id.code.upper(), 'CH')
        values.pop('country')
        fields = values.keys()
        expected_values = attrgetter(*fields)(customer)
        self.assertSequenceEqual(expected_values, values.values())

    def test3_update_customer(self):
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
        customer = self._o.model('res.partner').browse(customer_id)
        self.assertEqual(customer.country_id.code.upper(), 'FR')

    def test4_create_customer_address(self):
        pids = self._o.model('res.partner').search([('type', '=', 'default')])
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
        address = self._o.model('res.partner').browse(address_id)
        self.assertEqual(address.country_id.code.upper(), 'BE')
        values.pop('country')
        self.assertEqual(address.parent_id.id, partner_id)
        fields = values.keys()
        expected_values = attrgetter(*fields)(address)
        self.assertSequenceEqual(expected_values, values.values())

    def test5_update_customer(self):
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
        customer = self._o.model('res.partner').browse(address_id)
        self.assertEqual(customer.country_id.code.upper(), 'BE')

    def test6_create_sale_order(self):
        pids = self._o.model('res.partner').search([('type', '=', 'default')])
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
                #'order_line': order_line,
                }
        so_id = self.api.create_sale_order(SHOP_ID, values)
        #address = self._o.model('res.partner').browse(address_id)
        #self.assertEqual(address.country_id.code.upper(), 'BE')
        #values.pop('country')
        #self.assertEqual(address.parent_id.id, partner_id)
        #values.pop('parent_id')
        #fields = values.keys()
        #expected_values = attrgetter(*fields)(address)
        #self.assertSequenceEqual(expected_values, values.values())

if __name__ == '__main__':
    unittest2.main()

