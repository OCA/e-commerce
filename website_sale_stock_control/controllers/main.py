# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    def get_attribute_value_ids(self, product):
        res = super(WebsiteSale, self).get_attribute_value_ids(product)
        variant_ids = [r[0] for r in res]
        for r, variant in zip(
                res, request.env['product.product'].browse(variant_ids)):
            r.extend([variant.website_qty_available])
        return res

    def checkout_redirection(self, order):
        res = super(WebsiteSale, self).checkout_redirection(order=order)
        order = request.website.sale_get_order(context=request.context)
        lines = order.order_line.filtered(lambda x: (
            x.product_id.inventory_availability == 'always' and
            x.product_uom_qty > x.product_id.website_qty_available)
        )
        if lines:
            return request.redirect("/shop/cart")
        return res
