# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        parent_combination=False,
        only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )
        if variant_id := combination_info.get("product_id"):
            variant = self.env["product.product"].browse(variant_id)
            combination_info["default_product_packaging_level_name"] = (
                variant.from_default_level_packaging_id.name
            )
        else:
            combination_info["default_product_packaging_level_name"] = (
                self.from_default_level_packaging_id.name
            )
        return combination_info
