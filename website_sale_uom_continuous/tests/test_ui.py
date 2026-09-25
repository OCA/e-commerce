# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    def test_cart_quantity_decimals(self):
        washer, _powder = self.env["product.template"].create(
            [
                {
                    "name": "Decimal Washer",
                    "list_price": 1.0,
                    "website_published": True,
                },
                {
                    "name": "Decimal Powder",
                    "uom_id": self.env.ref("uom.product_uom_kgm").id,
                    "list_price": 10.0,
                    "website_published": True,
                },
            ]
        )
        self.env["product.template"].create(
            {
                "name": "Decimal Bolt",
                "list_price": 1.0,
                "website_published": True,
                # Opens the product configurator when added to the cart
                "optional_product_ids": [Command.set(washer.ids)],
            }
        )
        self.start_tour("/", "website_sale_uom_continuous", login="admin")
