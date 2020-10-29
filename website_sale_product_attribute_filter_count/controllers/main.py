# Copyright 2020 - Iván Todorovich
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductAttributeValues(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        res = super(ProductAttributeValues, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        # Avoid computing product counts if feature is not active
        website = request.env["website"].get_current_website()
        compute_counts = website.is_view_active(
            "website_sale_product_attribute_filter_count.products_attributes_count"
        ) or website.is_view_active(
            "website_sale_product_attribute_filter_count.products_attributes_existing"
        )
        if not compute_counts:
            return res
        # Search products without pager
        domain = self._get_search_domain(
            res.qcontext["search"],
            res.qcontext["category"],
            res.qcontext["attrib_values"],
        )
        Product = request.env["product.template"].with_context(bin_size=True)
        products = Product.search(domain)
        # Compute attrib_values_count
        attrib_values_count = {}
        attributes = res.qcontext["attributes"]
        if products and attributes:
            request.env.cr.execute(
                """
                SELECT
                    ptav.product_attribute_value_id,
                    count(distinct pp.product_tmpl_id)
                FROM product_product pp
                INNER JOIN product_variant_combination pvc
                    ON pvc.product_product_id = pp.id
                INNER JOIN product_template_attribute_value ptav
                    ON ptav.id = pvc.product_template_attribute_value_id
                WHERE
                        pp.active IS TRUE
                    AND ptav.attribute_id in %s
                    AND pp.product_tmpl_id in %s
                GROUP BY ptav.product_attribute_value_id
            """,
                [
                    tuple(attributes.ids),
                    tuple(products.ids),
                ],
            )
            attrib_values_count = dict(request.env.cr.fetchall())
        # Add results to context
        res.qcontext["attrib_values_count"] = attrib_values_count
        return res
