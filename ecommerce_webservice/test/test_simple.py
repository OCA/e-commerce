import csv
import sys
import datetime
import unittest2

import erppeek

ERPPEEK_TEST_ENV = "test"
MODULE_NAME = "ecommerce_webservice"

class BaseTest(unittest2.TestCase):

    def parse_csv(self, filename):
        records = csv.reader(open(filename, 'rb'))
        fieldnames = records.next()
        rows = [values for values in list(records) if values]
        return fieldnames, rows


class SmokeTest(BaseTest):

    def setUp(self):
        # init erppeek client
        #now = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        #template_db = 'test_%s' % MODULE_NAME
        #test_db = '%s_%s' % (template_db, now)
        #self._o = erppeek.Client.duplicate_database(template_db, test_db)
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
        self._o.model('res.users').load(f, r)

    def test1_create_shop(self):
        
        values = {
            'name': 'Unittest Generated Shop',
        }
        self.shop.create()

    #def test2_create_logs(self):
    #    values = {
    #        'shop_id'
    #    }
    #    self._o.model('ecommerce.api.log').create(values)

if __name__ == '__main__':
    unittest2.main()

