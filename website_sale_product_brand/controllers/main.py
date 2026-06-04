# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.fields import Domain
from odoo.http import request

from odoo.addons.website_sale.controllers.main import QueryURL, WebsiteSale


class WebsiteSale(WebsiteSale):
    def _update_domain(self, brands_list, domain):
        selected_brand_ids = [int(brand) for brand in brands_list]
        if brands_list:
            for leaf in domain:
                if leaf[0] == "product_brand_id":
                    domain.remove(leaf)
            domain += [("product_brand_id", "in", selected_brand_ids)]
        return domain

    def _get_brand_ids(self, req):
        return req.getlist("brand") or req.getlist("brand_ids") or []

    def _build_brands_list(
        self,
        selected_brand_ids,
        search=None,
        products=None,
        search_products=None,
        category=None,
    ):
        domain = []
        if not products:
            domain = [("id", "in", selected_brand_ids)]
        elif search or category:
            domain = [("product_ids", "in", search_products.ids)]
        return (
            request.env["product.brand"]
            .sudo()
            .search(domain)
            .filtered(lambda x: x.is_published and x.published_products_count > 0)
        )

    def _get_shop_domain_no_brands(
        self, search, category, attribute_value_dict, search_in_description
    ):
        return super()._get_shop_domain(
            search,
            category,
            attribute_value_dict,
            search_in_description=search_in_description,
        )

    def _remove_extra_brands(self, brands, search_products, attrib_values):
        if attrib_values:
            search_product_brands = search_products.mapped("product_brand_id")
            brands = brands.filtered(lambda b: b.id in search_product_brands.ids)
        # sort brands by name
        return brands.sorted(key=lambda brand: brand.name)

    def _get_search_options(
        self,
        category=None,
        attribute_value_dict=None,
        tags=None,
        min_price=0.0,
        max_price=0.0,
        conversion_rate=1,
        **post,
    ):
        res = super()._get_search_options(
            category=category,
            attribute_value_dict=attribute_value_dict,
            tags=tags,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post,
        )
        res["brand_ids"] = request.env.context.get("brand_ids")
        return res

    def _get_shop_domain(
        self, search, category, attribute_value_dict, search_in_description=True
    ):
        domain = super()._get_shop_domain(
            search,
            category,
            attribute_value_dict,
            search_in_description=search_in_description,
        )
        brand_ids = request.env.context.get("brand_ids") or [
            int(b)
            for b in (
                request.httprequest.args.getlist("brand")
                or request.httprequest.args.getlist("brand_ids")
            )
            if b and str(b).isdigit()
        ]
        if brand_ids:
            domain = Domain.AND([domain, [("product_brand_id", "in", brand_ids)]])
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
        **post,
    ):
        brands_list = self._get_brand_ids(request.httprequest.args)
        if brands_list:
            request.update_context(brand_ids=[int(b) for b in brands_list])
        elif brand:
            context = dict(request.env.context)
            context.setdefault("brand_ids", [int(brand)])
            request.update_context(**context)
        res = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            brand=brand,
            **post,
        )
        qcontext = getattr(res, "qcontext", None) or {}
        attrib_values = qcontext.get("attrib_values")
        products = qcontext.get("products")
        if attrib_values is None or products is None:
            return res
        attribute_values = request.httprequest.args.getlist("attribute_values")
        if attribute_values:
            post["attribute_values"] = attribute_values
        domain = self._get_shop_domain_no_brands(
            search, category, attrib_values, search_in_description=False
        )
        search_products = request.env["product.template"].search(domain)
        # build brands list
        selected_brand_ids = [int(brand) for brand in brands_list]
        brands = self._build_brands_list(
            selected_brand_ids, search, products, search_products, category
        )
        brands = self._remove_extra_brands(brands, search_products, attrib_values)
        # use search() domain instead of mapped() for better performance:
        # will basically search for product's related attribute values
        attrib_valid_ids = (
            request.env["product.attribute.value"]
            .search(
                [
                    "&",
                    (
                        "pav_attribute_line_ids.product_tmpl_id",
                        "in",
                        search_products._ids,
                    ),
                    ("pav_attribute_line_ids.value_ids", "!=", False),
                ]
            )
            .ids
        )
        keep = qcontext.get("keep")
        if keep and hasattr(keep, "args"):
            keep.args["brand"] = brands_list
            keep.args["brand_ids"] = selected_brand_ids
        # assign values for usage in qweb
        qcontext.update(
            {
                "brands": brands,
                "selected_brand_ids": selected_brand_ids,
                "attr_valid": attrib_valid_ids,
            }
        )
        return res

    # Method to get the brands.
    @http.route(["/page/product_brands"], type="http", auth="public", website=True)
    def product_brands(self, **post):
        b_obj = request.env["product.brand"]
        domain = [("website_published", "=", True)]
        if post.get("search"):
            domain += [("name", "ilike", post.get("search"))]
        brand_rec = (
            b_obj.sudo()
            .search(domain)
            .filtered(lambda x: x.published_products_count > 0)
        )

        keep = QueryURL("/page/product_brands", brand_id=[])
        values = {"brand_rec": brand_rec, "keep": keep}
        if post.get("search"):
            values.update({"search": post.get("search")})
        return request.render("website_sale_product_brand.product_brands", values)
