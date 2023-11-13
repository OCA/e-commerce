# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import TransactionCase


class SaleCase(TransactionCase):
    def setUp(self):
        super(SaleCase, self).setUp()
        self.demo_affiliate = self.env.ref(
            "website_sale_affiliate.sale_affiliate_myaffiliate"
        )
        self.demo_request = self.env.ref(
            "website_sale_affiliate.sale_affiliate_request_firesale"
        )
        self.demo_company = self.env.ref("base.main_company")
        self.demo_product = self.env.ref("product.product_product_4b")
