# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController as WebsiteSaleProductConfiguratorBase,
)


class WebsiteSaleProductConfiguratorController(WebsiteSaleProductConfiguratorBase):
    @staticmethod
    def _apply_taxes_to_price(price, product_or_template, currency):
        product_taxes = product_or_template.sudo().taxes_id._filter_taxes_by_company(
            request.env.company
        )
        if not product_taxes:
            return price
        if product_or_template._name == "product.product":
            template = product_or_template.product_tmpl_id
        else:
            template = product_or_template
        fiscal_position = request.website.fiscal_position_id.sudo().with_context(
            fp_template=template
        )
        taxes = fiscal_position.map_tax(product_taxes)
        return request.env["product.template"]._apply_taxes_to_price(
            price,
            currency,
            product_taxes,
            taxes,
            product_or_template,
            website=request.website,
        )
