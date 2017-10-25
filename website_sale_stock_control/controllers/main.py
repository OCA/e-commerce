# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    def get_attribute_value_ids(self, product):
        """Adds stock variants for render in shop."""
        res = super(WebsiteSale, self).get_attribute_value_ids(product)
        variant_ids = [r[0] for r in res]
        for r, variant in zip(
                res, request.env['product.product'].browse(variant_ids)):
            r.extend([variant.website_qty_available])
        return res

    def checkout_redirection(self, order):
        """Avoid the checkout if there's no stock of one of the
        products in the cart.
        """
        res = super(WebsiteSale, self).checkout_redirection(order=order)
        order = request.website.sale_get_order(context=request.context)
        lines = order.order_line.filtered(lambda x: (
            x.product_id.inventory_availability == 'always' and
            x.product_uom_qty > x.product_id.website_qty_available)
        )
        if lines:
            # redirecting again to the cart will show the text
            # "Temporarily out of stock"
            return request.redirect("/shop/cart")
        return res
