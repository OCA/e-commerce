# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

# Added for having easier customizations
COLUMN_LIMIT = 4
DEFAULT_PRICELIST_TITLE = "website_sale_product_minimal_price.pricelist_title"
DEFAULT_PRICELIST_SCALE = "website_sale_product_minimal_price.pricelist_scale"


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_product_pricelist_item_domain(self):
        self.ensure_one()
        return [
            "|",
            ("product_id", "=", self.id),
            "|",
            ("product_tmpl_id", "=", self.product_tmpl_id.id),
            (
                "categ_id",
                "in",
                list(map(int, self.categ_id.parent_path.split("/")[0:-1])),
            ),
            ("min_quantity", ">", 0),
        ]

    def _get_product_price_scale(self, qty_list):
        self.ensure_one()
        unit_prices = []
        last_price = self.with_context(quantity=0)._get_contextual_price()
        is_int = self.uom_id == self.env.ref("uom.product_uom_unit")
        for min_qty in qty_list:
            new_price = self.with_context(quantity=min_qty)._get_contextual_price()
            qty_min = int(min_qty) if is_int else min_qty
            if new_price != last_price and new_price != 0:
                unit_prices.append(
                    {
                        "qty_str": f"≥{qty_min}",
                        "qty_min": qty_min,  # Added for having easier customizations
                        "price": new_price,
                        "currency_id": self.currency_id.id,
                    }
                )
                last_price = new_price

        return {
            "uom": self.uom_name,
            "column_limit": COLUMN_LIMIT,
            "pricelist_title": DEFAULT_PRICELIST_TITLE,
            "pricelist_scale": DEFAULT_PRICELIST_SCALE,
            "unit_prices": unit_prices,
        }
