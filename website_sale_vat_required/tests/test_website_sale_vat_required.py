# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class TestWebsiteSaleVatRequired(HttpCase):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.template"].create(
            {
                "name": "Test Product Vat Required",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
                "list_price": 10.0,
            }
        )

    def test_website_sale_vat_required(self):
        self.start_tour("/shop", "website_sale_vat_required_tour")
