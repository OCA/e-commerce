# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _apply_taxes_to_price(
        self, price, currency, product_taxes, taxes, product_or_template
    ):
        """Website prices follow the website setting, not the user groups
        (which `res.users.has_group` overrides), so apply the toggle here."""
        taxed = request.session.get("tax_toggle_taxed") if request else None
        if taxed is None:
            return super()._apply_taxes_to_price(
                price, currency, product_taxes, taxes, product_or_template
            )
        price = self.env["product.product"]._get_tax_included_unit_price_from_price(
            price, currency, product_taxes, product_taxes_after_fp=taxes
        )
        tax_display = "total_included" if taxed else "total_excluded"
        return taxes.compute_all(
            price, currency, 1, product_or_template, self.env.user.partner_id
        )[tax_display]
