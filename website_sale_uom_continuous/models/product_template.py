# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, uom, date, website
    ):
        # OVERRIDE: let the product page only allow decimal quantities for
        # continuous UoMs.
        combination_info = super()._get_additionnal_combination_info(
            product_or_template, quantity, uom, date, website
        )
        combination_info["uom_is_continuous"] = uom._is_continuous()
        return combination_info
