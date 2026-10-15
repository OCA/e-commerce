# Copyright 20202520 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.http import request
from odoo.tools import config


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _apply_taxes_to_price(
        self,
        price,
        currency,
        product_taxes,
        taxes,
        product_or_template,
        website=None,
    ):
        res = super()._apply_taxes_to_price(
            price, currency, product_taxes, taxes, product_or_template, website
        )
        test_condition = not config["test_enable"] or (
            config["test_enable"]
            and self.env.context.get("test_website_sale_tax_toggle")
        )
        if not website or not test_condition:
            return res
        price = self.env["product.product"]._get_tax_included_unit_price_from_price(
            price,
            product_taxes,
            product_taxes_after_fp=taxes,
        )
        show_tax = request.session.get("tax_toggle_taxed")
        tax_display = "total_included" if show_tax else "total_excluded"
        return taxes.compute_all(
            price, currency, 1, product_or_template, self.env.user.partner_id
        )[tax_display]
