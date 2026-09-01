# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
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
        hide_price = (
            website.website_hide_price
            or not self.env.user.partner_id.website_show_price
            or combination_info.get("website_hide_price", False)
        )
        if hide_price:
            combination_info["minimal_price_scale"] = []
        return combination_info
