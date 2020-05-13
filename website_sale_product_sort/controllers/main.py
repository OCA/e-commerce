# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    def _get_search_order(self, post):
        """We can configure default sort criteria for every website"""
        return "website_published desc,%s , id desc" % post.get(
            "order", request.website.default_product_sort_criteria
        )

    @route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        """We can configure default sort criteria for every website"""
        response = super().shop(
            page=page, category=category, search=search, **post
        )
        response.qcontext["order"] = post.get(
            "order", request.website.default_product_sort_criteria)
        return response
