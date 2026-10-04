# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


class WebsiteSaleUomContinuousCommon(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_kg = cls.env["product.product"].create(
            {
                "name": "Powder",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "list_price": 10.0,
                "sale_ok": True,
                "website_published": True,
            }
        )
        # Sold in units and packs of 6, at 5.0 per unit from 20 units
        cls._enable_uom()
        cls.product_pack = cls.env["product.product"].create(
            {
                "name": "Bottle",
                "uom_ids": [Command.set(cls.uom_pack_6.ids)],
                "list_price": 10.0,
                "sale_ok": True,
                "website_published": True,
            }
        )
        cls.pricelist.item_ids = [
            Command.create(
                {
                    "applied_on": "1_product",
                    "product_tmpl_id": cls.product_pack.product_tmpl_id.id,
                    "min_quantity": 20,
                    "compute_price": "fixed",
                    "fixed_price": 5.0,
                }
            )
        ]
