# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import MockRequest

from ..controllers.product_configurator import (
    WebsiteSaleUomContinuousProductConfiguratorController,
)
from .common import WebsiteSaleUomContinuousCommon


@tagged("post_install", "-at_install")
class TestProductConfigurator(WebsiteSaleUomContinuousCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = WebsiteSaleUomContinuousProductConfiguratorController()

    def test_quantity_by_uom(self):
        """The configurator only allows decimal quantities for continuous UoMs.

        Scenario:
            1. Open the configurator of a product sold in units, with 1.5 units.
            2. Open the configurator of a product sold in kg, with 2.555 kg.
        Expected:
            - The configurator opens with 1 unit, and a UoM that is not continuous.
            - The configurator opens with 2.56 kg, and a continuous UoM.
        """
        for product, quantity, expected_quantity, is_continuous in (
            (self.product, 1.5, 1, False),
            (self.product_kg, 2.555, 2.56, True),
        ):
            with MockRequest(self.env, website=self.website):
                values = self.controller.website_sale_product_configurator_get_values(
                    product_template_id=product.product_tmpl_id.id,
                    quantity=quantity,
                    currency_id=self.currency.id,
                    so_date="2000-01-01",
                    pricelist_id=self.pricelist.id,
                )
            product_values = values["products"][0]
            self.assertEqual(product_values["quantity"], expected_quantity)
            self.assertEqual(product_values["uom"]["is_continuous"], is_continuous)
