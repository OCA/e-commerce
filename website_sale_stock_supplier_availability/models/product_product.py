# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_sold_out(self) -> bool:
        res = super()._is_sold_out()
        sellers = self.seller_ids.filtered(lambda s: s.stock_availability)
        if sellers:
            return bool(
                res
                and any(
                    seller.stock_availability == "unavailable" for seller in sellers
                )
            )
        return res
