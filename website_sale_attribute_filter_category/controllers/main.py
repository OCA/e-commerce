# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import _, http


class ProductAttributeCategory(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response = super(ProductAttributeCategory, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        # Re-order attributes by their category sequence
        response.qcontext['attributes'] = (
            response.qcontext['attributes'].sorted(
                lambda x: (x.category_id.sequence, x.id)))
        # Load all categories, and load a "False" category for attributes that
        # has not category and display it under 'Undefined' category
        categories = [(False, _('Undefined'), True)]
        categories.extend(
            (x.id,
             x.name,
             x.website_folded
             ) for x in response.qcontext['attributes'].mapped('category_id'))
        response.qcontext['attribute_categories'] = categories
        response.qcontext['filtered_products'] = False
        if search or post.get('attrib', False):
            response.qcontext['filtered_products'] = True
        return response
