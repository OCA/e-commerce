# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http


class ProductAttributeValues(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        # Store used domain in context to be reused after
        domain = super(ProductAttributeValues, self)._get_search_domain(
            search, category, attrib_values)
        new_context = dict(request.env.context, shop_search_domain=domain)
        request.context = new_context
        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(ProductAttributeValues, self).shop(
            page=page,
            category=category,
            search=search,
            ppg=ppg,
            **post)
        domain = request.env.context.get('shop_search_domain', [])
        # Load all products without limit for the filter check on
        # attribute values
        templates = request.env['product.template'].search(
            domain, limit=False)
        ProductTemplateAttributeLine = request.env[
            'product.template.attribute.line']
        attribute_values = ProductTemplateAttributeLine.search([
            ('product_tmpl_id', 'in', templates.ids),
        ])
        res.qcontext['attr_values_used'] = attribute_values.mapped('value_ids')
        return res
