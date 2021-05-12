# Copyright 2021 Manuel Calero <https://xtendoo.es/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductAttributeCategory(WebsiteSale):
    @route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        if not category and request.website.init_category_id:
            category = request.website.init_category_id
        response = super(ProductAttributeCategory, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        return response
