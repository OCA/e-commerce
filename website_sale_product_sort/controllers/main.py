# Copyright 2020 Tecnativa - David Vidal
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_search_order(self, post):
        """We can configure default sort criteria for every website"""
        if post.get("order"):
            return super()._get_search_order(post)
        order = request.website.default_product_sort_criteria
        return f"is_published desc, {order}, id desc"

    @route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        """Transfer custom sort order to QWeb templates."""
        response = super().shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        response.qcontext["order"] = (
            post.get("order") or request.website.default_product_sort_criteria
        )
        return response
