# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.addons.website_sale.tests.common import MockRequest

from ..controllers.cart import WebsiteSaleUomContinuousCart
from .common import WebsiteSaleUomContinuousCommon


@tagged("post_install", "-at_install")
class TestCombinationInfo(WebsiteSaleUomContinuousCommon):
    def test_uom_is_continuous(self):
        """The combination info tells whether the UoM allows decimal quantities."""
        with MockRequest(self.env, website=self.website):
            info = self.product._get_combination_info_variant()
            self.assertFalse(info["uom_is_continuous"])
            info = self.product_kg._get_combination_info_variant()
            self.assertTrue(info["uom_is_continuous"])

    def test_price_integer_quantity(self):
        """The displayed price is the one of the quantity added to the cart.

        Scenario:
            1. Get the price of 3.7 packs of 6 of a product at 5.0 per unit from 20
               units, and 10.0 otherwise.
            2. Add 3.7 packs of 6 of this product to the cart.
        Expected:
            - The price is the one of 3 packs (18 units): 60.0 per pack.
            - The cart line holds 3 packs, at the same price.
        """
        with MockRequest(self.env, website=self.website) as request:
            info = WebsiteSaleVariantController().get_combination_info_website(
                product_template_id=self.product_pack.product_tmpl_id.id,
                product_id=self.product_pack.id,
                combination=[],
                add_qty=3.7,
                uom_id=self.uom_pack_6.id,
            )
            WebsiteSaleUomContinuousCart().add_to_cart(
                product_template_id=self.product_pack.product_tmpl_id.id,
                product_id=self.product_pack.id,
                quantity=3.7,
                uom_id=self.uom_pack_6.id,
            )
            line = request.cart.order_line
        self.assertEqual(info["price"], 60.0)
        self.assertEqual(line.product_uom_id, self.uom_pack_6)
        self.assertEqual(line.product_uom_qty, 3)
        self.assertEqual(line.price_unit, info["price"])
