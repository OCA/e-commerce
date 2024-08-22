# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo.http import request, route

from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleAssortment(WebsiteSale):
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
                partner & assortment.with_context(active_test=False).all_partner_ids
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

    def _get_search_options(
        self,
        category=None,
        attrib_values=None,
        pricelist=None,
        min_price=0.0,
        max_price=0.0,
        conversion_rate=1,
        **post,
    ):
        """Overriding _get_search_options method to avoid show product templates that
        has all their variants not allowed to be shown."""
        res = super()._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post,
        )
        allowed_product_ids, assortment_restriction = self._get_products_allowed()
        if assortment_restriction:
            res["allowed_product_domain"] = [
                ("product_variant_ids", "in", list(allowed_product_ids))
            ]
        return res


class WebsiteAssortment(Website):
    @route()
    def autocomplete(
        self,
        search_type=None,
        term=None,
        order=None,
        limit=5,
        max_nb_chars=999,
        options=None,
    ):
        (
            allowed_product_ids,
            assortment_restriction,
        ) = WebsiteSaleAssortment._get_products_allowed(self)
        if assortment_restriction:
            options["allowed_product_domain"] = [
                ("product_variant_ids", "in", list(allowed_product_ids))
            ]

        return super().autocomplete(
            search_type=search_type,
            term=term,
            order=order,
            limit=limit,
            max_nb_chars=max_nb_chars,
            options=options,
        )
