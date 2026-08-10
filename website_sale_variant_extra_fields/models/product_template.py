# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        uom_id=False,
        only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            uom_id=uom_id,
            only_template=only_template,
        )
        website = self.env["website"].get_current_website()
        extra_fields = website.shop_extra_field_ids.filtered("is_variant_field")
        if not extra_fields:
            return combination_info
        variant = self.env["product.product"].browse(combination_info.get("product_id"))
        combination_info["variant_extra_fields"] = extra_fields._get_rendered_values(
            variant
        )
        return combination_info
