# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import QueryURL, WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_search_options(
        self,
        category=None,
        attrib_values=None,
        pricelist=None,
        min_price=0.0,
        max_price=0.0,
        conversion_rate=1,
        **post
    ):
        res = super()._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post
        )
        res["brand"] = request.context.get("brand_id")
        return res

    def _get_search_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        domain = super()._get_search_domain(
            search, category, attrib_values, search_in_description=search_in_description
        )
        if "brand_id" in request.context:
            domain = expression.AND(
                [domain, [("product_brand_id", "=", request.context["brand_id"])]]
            )
        return domain

    @http.route(
        [
            "/shop",
            "/shop/page/<int:page>",
            '/shop/category/<model("product.public.category"):category>',
            '/shop/category/<model("product.public.category"):category'
            ">/page/<int:page>",  # Continue previous line
            "/shop/brands",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        brand=None,
        **post
    ):
        if brand:
            context = dict(request.context)
            context.setdefault("brand_id", int(brand))
            request.update_context(**context)
        return super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            brand=brand,
            **post
        )

    # Method to get the brands.
    @http.route(["/page/product_brands"], type="http", auth="public", website=True)
    def product_brands(self, **post):
        b_obj = request.env["product.brand"]
        domain = [("website_published", "=", True)]
        if post.get("search"):
            domain += [("name", "ilike", post.get("search"))]
        brand_rec = b_obj.sudo().search(domain)

        keep = QueryURL("/page/product_brands", brand_id=[])
        values = {"brand_rec": brand_rec, "keep": keep}
        if post.get("search"):
            values.update({"search": post.get("search")})
        return request.render("website_sale_product_brand.product_brands", values)
