import csv
import sys
import datetime
import unittest2

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
        #    self._o = connect to test_db
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
                'parent_id': False,
                'active': True,
                'street': 'of Philadelphia',
                'street2': 'empty',
                'city': 'Sin',
                'zip': '1040',
                'country': 'CH',
                'type': 'default',
                'phone': '555-123456',
                'mobile': '555-987654',
                'fax': 'no fax',
                'email': 'john.smith@example.com',
                }
        customer_id = self.api.create_customer(SHOP_ID, values)
        self.assertGreater(customer_id, 1)

if __name__ == '__main__':
    unittest2.main()

