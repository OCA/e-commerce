# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore, LLC
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _website_price(self):
        super(ProductProduct, self)._website_price()
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        pricelist = self.env['website'].\
            get_current_website().get_current_pricelist()

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) \
            if self._context != context else self

        ret = self.env.user.has_group('sale.group_show_price_subtotal') and \
            'total_excluded' or 'total_included'

        for p, p2 in zip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.taxes_id)
            p.website_price = \
                taxes.compute_all(
                    p2.price*qty,
                    pricelist.currency_id,
                    quantity=qty,
                    product=p2,
                    partner=partner)[ret]
            p.website_public_price = taxes.compute_all(p2.lst_price*qty,
                                                       quantity=qty,
                                                       product=p2,
                                                       partner=partner)[ret]
