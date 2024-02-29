from odoo import http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFormSupplierInfo(WebsiteSale):
    def _get_search_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        res = super()._get_search_domain(
            search, category, attrib_values, search_in_description
        )
        res = expression.OR(
            [
                res,
                [
                    "&",
                    ("customer_ids.name", "=", request.env.user.partner_id.id),
                    ("customer_ids.product_name", "ilike", search),
                ],
            ]
        )
        return res

    @http.route()
    def products_autocomplete(self, term, options=None, **kwargs):
        if options is None:
            options = {}
        res = super().products_autocomplete(term, options, **kwargs)
        products = res.get("products", [])
        for product in products:
            product["name"] = product["display_name"]
        return res
