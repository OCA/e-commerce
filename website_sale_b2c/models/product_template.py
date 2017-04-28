# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # HACK Redefine computation or we cannot override it
    price = fields.Float(compute="_product_template_price")

    @api.model
    def _price_b2c_wrapper(self, products, prices):
        result = prices.copy()
        if self.env.context.get("b2c_prices"):
            qty = self.env.context.get("quantity", 1.0)
            partner = self.env.user.partner_id
            website = self.env['website'].get_current_website()
            pricelist = website.get_current_pricelist()
            products = products.with_context(
                partner=self.env.user.partner_id,
                pricelist=pricelist.id,
            )
            website = self.env['website'].browse(
                self.env.context.get('website_id'))
            for product_id, price in result.iteritems():
                product = products.browse(product_id)
                taxes = partner.property_account_position_id.map_tax(
                    product.taxes_id.filtered(
                        lambda x: x.company_id == website.company_id))
                result[product_id] = taxes.compute_all(
                    price,
                    pricelist.currency_id,
                    qty,
                    product,
                    partner,
                )["total_included"]
        return result

    @api.model
    def _product_template_price(self):
        result = self._price_b2c_wrapper(
            self,
            super(ProductTemplate, self)._product_template_price(
                "price",
                None,
            )
        )
        for one in self:
            one.price = result[one.id]
