# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo.http import request, route
from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_products_allowed(self):
        partner = request.env.user.partner_id
        website_id = request.website.id
        assortments = (
            request.env["ir.filters"]
            .sudo()
            .search(
                [
                    ("is_assortment", "=", True),
                    ("website_availability", "=", "no_show"),
                    "|",
                    ("website_ids", "=", False),
                    ("website_ids", "=", website_id),
                ]
            )
        )
        assortment_restriction = False
        allowed_product_ids = set()
        for assortment in assortments:
            if (
                # Set active_test to False to allow filtering by partners
                # that are not active, (for example Public User)
                partner
                & assortment.with_context(active_test=False).all_partner_ids
            ):
                assortment_restriction = True
                allowed_product_ids = allowed_product_ids.union(
                    set(assortment.all_product_ids.ids)
                )
        return allowed_product_ids, assortment_restriction

    @route()
    def product(self, product, category="", search="", **kwargs):
        """Overriding product method to avoid accessing to product sheet when the
        product assortments prevent to show them.
        """
        allowed_product_ids, assortment_restriction = self._get_products_allowed()
        if assortment_restriction:
            if len(set(product.product_variant_ids.ids) & allowed_product_ids) == 0:
                raise NotFound()
        return super().product(product, category=category, search=search, **kwargs)

    def _get_search_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        """Overriding _get_search_domain method to avoid show product templates that
        has all their variants not allowed to be shown.
        """
        res = super()._get_search_domain(
            search, category, attrib_values, search_in_description=search_in_description
        )
        allowed_product_ids, assortment_restriction = self._get_products_allowed()
        if assortment_restriction:
            return expression.AND(
                [res, [("product_variant_ids", "in", list(allowed_product_ids))]]
            )
        return res
