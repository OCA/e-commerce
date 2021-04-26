# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleForceQtyTest(HttpCase):

    def setUp(self):
        super().setUp()
        att_color = self.env["product.attribute"].create({
            'name': 'color_test',
        })
        att_color_blue = self.env["product.attribute.value"].create({
            'name': 'Blue',
            'attribute_id': att_color.id,
        })
        att_color_red = self.env["product.attribute.value"].create({
            'name': 'Red',
            'attribute_id': att_color.id,
        })
        self.env["product.template"].create([
            {
                "name": "Test product with fixed quantity",
                "website_sale_force_qty": 2.0,
                "website_published": True,
                "website_sequence": 100,
            },
            {
                "name": "Test product with variants, optionals and fixed quantity",
                "website_sale_force_qty": 3.0,
                "website_published": True,
                "website_sequence": 101,
                "optional_product_ids": [(0, 0, {
                    "name": "Optional product",
                    "website_published": True,
                })],
                "attribute_line_ids": [(0, 0, {
                    "attribute_id": att_color.id,
                    "value_ids": [
                        (4, att_color_blue.id),
                        (4, att_color_red.id),
                    ],
                })],
            },
            {
                "name": "Test product normal",
                "website_published": True,
                "website_sequence": 102,
            },
        ])

    def test_ui(self):
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_force_qty",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="portal",
        )
