# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request  # type: ignore[import]
from odoo.tools import str2bool  # type: ignore[import]

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleRestrictByPricelistController(WebsiteSale):
    def _is_restriction_enabled_for_user(self):
        user = request.env.user
        restrict_products_for_all_users = str2bool(
            request.env["ir.config_parameter"].sudo().get_param(
                "website_sale_restrict_by_pricelist.restrict_products",
                default="False",
            )
        )
        return user.has_group("base.group_portal") and (
            user.restrict_products or restrict_products_for_all_users
        )

    def _get_allowed_product_domain(self):
        if not self._is_restriction_enabled_for_user():
            return []

        pricelist = request.env.user.property_product_pricelist
        if not pricelist:
            return [("id", "=", 0)]

        items = pricelist.item_ids
        if not items:
            return [("id", "=", 0)]

        # A global item means "all products"; no additional product-id restriction.
        if items.filtered(lambda item: item.applied_on == "3_global"):
            return []

        allowed_templates = request.env["product.template"]
        product_items = items.filtered(lambda item: item.applied_on == "1_product")
        allowed_templates |= product_items.mapped("product_tmpl_id")

        variant_items = items.filtered(lambda item: item.applied_on == "0_product_variant")
        allowed_templates |= variant_items.mapped("product_id.product_tmpl_id")

        category_items = items.filtered(
            lambda item: item.applied_on == "2_product_category"
        )
        category_ids = category_items.mapped("categ_id").ids
        if category_ids:
            allowed_templates |= request.env["product.template"].search(
                [("categ_id", "child_of", category_ids)]
            )

        if not allowed_templates:
            return [("id", "=", 0)]

        return [("id", "in", allowed_templates.ids)]

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        fuzzy_search_term, product_count, search_product = super()._shop_lookup_products(
            attrib_set, options, post, search, website
        )
        allowed_domain = self._get_allowed_product_domain()
        if allowed_domain:
            search_product = search_product.filtered_domain(allowed_domain)
            product_count = len(search_product)
        return fuzzy_search_term, product_count, search_product

    def _get_search_domain(  # type: ignore[override]
        self, search, category, attrib_values, search_in_description=True
    ):
        domain = super()._get_search_domain(
            search, category, attrib_values, search_in_description=search_in_description
        )
        allowed_domain = self._get_allowed_product_domain()
        if not allowed_domain:
            return domain
        return domain + allowed_domain
