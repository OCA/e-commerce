# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import MockRequest

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
