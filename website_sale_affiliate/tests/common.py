# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import time

from odoo.http import _request_stack
from odoo.tests.common import TransactionCase
from odoo.tools import DotDict


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

        fake_req = DotDict(
            {
                # various things go and access request items
                "httprequest": DotDict(
                    {
                        "headers": {
                            "environ": {
                                "REMOTE_ADDR": "0.0.0.0",
                                "HTTP_REFERER": "referer",
                                "HTTP_USER_AGENT": "user agent",
                                "HTTP_ACCEPT_LANGUAGE": "Language",
                            },
                        },
                        "cookies": {},
                    }
                ),
                # bypass check_identity flow
                "session": {"identity-check-last": time.time(), "affiliate_request": 1},
            }
        )
        _request_stack.push(fake_req)
        self.addCleanup(_request_stack.pop)
