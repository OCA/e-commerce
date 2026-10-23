# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models

from odoo.addons.website.models import ir_http


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_sales_prices(self, website):
        res = {}
        for template in self:
            website = website.with_context(fp_template=template)
            res.update(super(ProductTemplate, template)._get_sales_prices(website))
        return res

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, date, website
    ):
        template = self.env["product.template"]
        if product_or_template._name == "product.product":
            template = product_or_template.product_tmpl_id
        elif product_or_template._name == "product.template":
            template = product_or_template
        if template:
            website = website.with_context(fp_template=template)
        return super()._get_additionnal_combination_info(
            product_or_template, quantity, date, website
        )

    @api.model
    def _get_configurator_display_price(
        self, product_or_template, quantity, date, currency, pricelist, **kwargs
    ):
        price, pricelist_rule_id = self._get_configurator_price(
            product_or_template, quantity, date, currency, pricelist, **kwargs
        )
        website = ir_http.get_request_website()
        if not website:
            return price, pricelist_rule_id
        product_taxes = product_or_template.sudo().taxes_id._filter_taxes_by_company(
            self.env.company
        )
        if not product_taxes:
            return price, pricelist_rule_id
        if product_or_template._name == "product.product":
            template = product_or_template.product_tmpl_id
        else:
            template = product_or_template
        fiscal_position = website.fiscal_position_id.sudo().with_context(
            fp_template=template
        )
        taxes = fiscal_position.map_tax(product_taxes)
        return (
            self._apply_taxes_to_price(
                price,
                currency,
                product_taxes,
                taxes,
                product_or_template,
                website=website,
            ),
            pricelist_rule_id,
        )
