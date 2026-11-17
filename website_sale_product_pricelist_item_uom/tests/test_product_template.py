# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import tagged

from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon


@tagged("post_install", "-at_install")
class TestProductTemplatePackagingPrices(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ``_has_multiple_uoms`` is only true when the packagings feature is on.
        cls.env.ref("base.group_user").implied_ids |= cls.env.ref("uom.group_uom")
        cls._enable_pricelists()

        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Packaging Product",
                "list_price": 100.0,
                "uom_id": cls.uom_unit.id,
                "uom_ids": [Command.link(cls.uom_pack_6.id)],
                "is_published": True,
            }
        )
        cls.env["product.pricelist.item"].create(
            [
                {
                    "pricelist_id": cls.pricelist.id,
                    "applied_on": "1_product",
                    "product_tmpl_id": cls.product_tmpl.id,
                    "compute_price": "fixed",
                    "fixed_price": 10.0,
                    "uom_id": cls.uom_unit.id,
                },
                {
                    "pricelist_id": cls.pricelist.id,
                    "applied_on": "1_product",
                    "product_tmpl_id": cls.product_tmpl.id,
                    "compute_price": "fixed",
                    "fixed_price": 8.0,
                    "uom_id": cls.uom_pack_6.id,
                },
            ]
        )

    def test_combination_info_packaging_prices(self):
        """Each packaging price is returned, expressed in the product base UoM."""
        with MockRequest(
            self.env, website=self.website, website_sale_current_pl=self.pricelist.id
        ):
            combination_info = self.product_tmpl._get_combination_info()

        packaging_prices = combination_info["packaging_prices"]
        self.assertEqual(set(packaging_prices), {self.uom_unit.id, self.uom_pack_6.id})
        self.assertEqual(packaging_prices[self.uom_unit.id], 10.0)
        self.assertEqual(packaging_prices[self.uom_pack_6.id], 8.0)

    def test_combination_info_without_packaging(self):
        """Products sold in a single UoM get no packaging price."""
        self.product_tmpl.uom_ids = [Command.clear()]

        with MockRequest(
            self.env, website=self.website, website_sale_current_pl=self.pricelist.id
        ):
            combination_info = self.product_tmpl._get_combination_info()

        self.assertNotIn("packaging_prices", combination_info)
