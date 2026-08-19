# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductAttributeCategory(WebsiteSale):
    @http.route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        tags="",
        **post,
    ):
        response = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            **post,
        )
        if "attributes" not in response.qcontext:
            # `shop()` can return an early redirect (ecommerce access check,
            # legacy category-in-query redirect, another module's override...)
            # instead of the rendered "website_sale.products" response.
            return response
        # Re-order attributes by their category sequence
        response.qcontext["attributes"] = response.qcontext["attributes"].sorted(
            lambda x: (x.category_id.sequence, x.id)
        )
        # Load all categories, and load a "False" category for attributes that
        # has not category and display it under 'Undefined' category
        categories = [(False, request.env._("Undefined"), True)]
        categories.extend(
            (x.id, x.name, x.website_folded)
            for x in response.qcontext["attributes"].mapped("category_id")
        )
        response.qcontext["attribute_categories"] = categories
        response.qcontext["filtered_products"] = False
        if search or post.get("attribute_values", False):
            response.qcontext["filtered_products"] = True
        return response
