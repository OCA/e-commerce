# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
