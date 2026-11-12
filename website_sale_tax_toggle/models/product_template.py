# Copyright 20202520 Tecnativa - Pilar Vargas
# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.http import request
from odoo.modules import module
from odoo.tools import config


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _apply_taxes_to_price(
        self,
        price,
        currency,
        *,
        product=None,
        product_taxes=None,
        taxes=None,
        tax_display=None,
        website=None,
    ):
        if not config["test_enable"] or (
            config["test_enable"]
            and module.current_test.test_module == "website_sale_tax_toggle"
        ):
            tax_display = (
                "total_included"
                if request.session.get("tax_toggle_taxed", False)
                else "total_excluded"
            )
        return super()._apply_taxes_to_price(
            price,
            currency,
            product=product,
            product_taxes=product_taxes,
            taxes=taxes,
            tax_display=tax_display,
            website=website,
        )
