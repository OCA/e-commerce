# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib.parse import urlencode

from odoo import http
from odoo.fields import Domain
from odoo.http import request

from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_sale.const import SHOP_PATH
from odoo.addons.website_sale.controllers.main import (
    QueryURL,
)
from odoo.addons.website_sale.controllers.main import (
    WebsiteSale as WebsiteSaleBase,
)


class WebsiteSale(WebsiteSaleBase):
    def _as_int_list(self, values):
        return [int(value) for value in values if str(value).isdigit()]

    def _get_brand_from_query(self, query_args, fallback_brand=None):
        brand_value = (
            query_args.get("brand") or query_args.get("brand_ids") or fallback_brand
        )
        if isinstance(brand_value, (list, tuple)):
            brand_value = brand_value[0] if brand_value else None
        brand_id = int(brand_value) if str(brand_value).isdigit() else None
        if not brand_id:
            return request.env["product.brand"]
        return request.env["product.brand"].browse(brand_id)

    def _get_brand_from_slug(self, brand_slug):
        brand_id = request.env["ir.http"]._unslug(brand_slug)[1]
        return request.env["product.brand"].browse(brand_id)

    def _get_current_brand(self):
        return getattr(request, "_website_sale_brand", request.env["product.brand"])

    def _set_current_brand(self, brand):
        request._website_sale_brand = brand

    def _clear_current_brand(self):
        if hasattr(request, "_website_sale_brand"):
            delattr(request, "_website_sale_brand")

    def _brand_visible_on_website(self, brand):
        if not (brand and brand.website_published):
            return False
        return brand.can_access_from_current_website()

    def sitemap_brands(env, rule, qs):
        website = env["website"].get_current_website()
        if website and website.ecommerce_access == "logged_in" and not qs:
            return

        product_brand_model = env["product.brand"]
        domain = sitemap_qs2dom(qs, f"{SHOP_PATH}/brand", product_brand_model._rec_name)
        domain &= product_brand_model._website_public_domain(website=website)
        for brand in product_brand_model.search(domain):
            loc = f"{SHOP_PATH}/brand/{env['ir.http']._slug(brand)}"
            if not qs or qs.lower() in loc:
                yield {"loc": loc}

    def _get_shop_path(self, category=None, page=0):
        path = WebsiteSaleBase._get_shop_path(category=category, page=page)
        brand = self._get_current_brand()
        if brand:
            path = f"{SHOP_PATH}/brand/{request.env['ir.http']._slug(brand)}"
            if page:
                path += f"/page/{page}"
        return path

    def _update_domain(self, brands_list, domain):
        selected_brand_ids = self._as_int_list(brands_list)
        if not selected_brand_ids:
            return domain
        domain_no_brand = [
            leaf
            for leaf in domain
            if not (
                isinstance(leaf, (list, tuple))
                and leaf
                and leaf[0] == "product_brand_id"
            )
        ]
        return domain_no_brand + [("product_brand_id", "in", selected_brand_ids)]

    def _get_brand_ids(self, req):
        raw_brand_ids = req.getlist("brand") or req.getlist("brand_ids") or []
        return self._as_int_list(raw_brand_ids)

    def _build_brands_list(
        self,
        selected_brand_ids,
        search=None,
        products=None,
        search_products=None,
        category=None,
    ):
        brand_model = request.env["product.brand"].sudo()
        domain = brand_model._website_public_domain()
        if not products:
            domain = Domain.AND([domain, [("id", "in", selected_brand_ids)]])
        elif search or category:
            domain = Domain.AND([domain, [("product_ids", "in", search_products.ids)]])
        return brand_model.search(domain).filtered(
            lambda x: x.published_products_count > 0
            or x.show_without_published_products
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
        brand_ids = request.env.context.get("brand_ids") or self._get_brand_ids(
            request.httprequest.args
        )
        if brand_ids:
            domain = Domain.AND([domain, [("product_brand_id", "in", brand_ids)]])
        return domain

    def _redirect_shop_brands_to_landing(self, fallback_brand=None):
        """
        When accessing `/shop/brands` with a `brand` or `brand_ids`
        query parameter, redirect to the corresponding brand landing page
        if the brand is published on the website.
        This allows external links to `/shop/brands?brand=1` to be redirected
        to the brand landing page, and also allows the shop page to redirect
        to the brand landing page when a brand is selected from the brands list.
        """
        if not request.httprequest.path.endswith(f"{SHOP_PATH}/brands"):
            return None

        landing_brand = self._get_brand_from_query(
            request.httprequest.args, fallback_brand
        )
        if not landing_brand:
            return None
        if not self._brand_visible_on_website(landing_brand):
            raise request.not_found()

        query_args = request.httprequest.args.to_dict(flat=False)
        query_args.pop("brand", None)
        query_args.pop("brand_ids", None)
        query = urlencode(query_args, doseq=True)
        target = landing_brand.website_url
        if query:
            target = f"{target}?{query}"
        return request.redirect(target, code=301)

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
        redirect_response = self._redirect_shop_brands_to_landing(brand)
        if redirect_response is not None:
            return redirect_response

        brands_list = self._get_brand_ids(request.httprequest.args)
        if brands_list:
            request.update_context(brand_ids=brands_list)
        elif brand:
            fallback_brand_ids = self._as_int_list([brand])
            if fallback_brand_ids:
                request.update_context(brand_ids=fallback_brand_ids)
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
        selected_brand_ids = brands_list
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

    @http.route(
        [
            f"{SHOP_PATH}/brand/<string:brand_slug>",
            f"{SHOP_PATH}/brand/<string:brand_slug>/page/<int:page>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=sitemap_brands,
    )
    def shop_brand(
        self,
        brand_slug,
        page=0,
        search="",
        min_price=0.0,
        max_price=0.0,
        tags="",
        **post,
    ):
        brand = self._get_brand_from_slug(brand_slug)

        if not request.website.has_ecommerce_access():
            return request.redirect(f"/web/login?redirect={request.httprequest.path}")
        if not self._brand_visible_on_website(brand):
            raise request.not_found()

        self._set_current_brand(brand)
        request.update_context(brand_ids=[brand.id])
        try:
            response = super().shop(
                page=page,
                category=None,
                search=search,
                min_price=min_price,
                max_price=max_price,
                tags=tags,
                **post,
            )
            if hasattr(response, "qcontext"):
                response.qcontext.update(
                    {
                        "landing_brand": brand,
                        "main_object": brand,
                    }
                )
            return response
        finally:
            self._clear_current_brand()

    # Method to get the brands.
    @http.route(["/page/product_brands"], type="http", auth="public", website=True)
    def product_brands(self, **post):
        product_brand = request.env["product.brand"]
        domain = product_brand._website_public_domain()
        if post.get("search"):
            domain = Domain.AND([domain, [("name", "ilike", post.get("search"))]])
        brand_rec = (
            product_brand.sudo()
            .search(domain)
            .filtered(
                lambda x: x.published_products_count > 0
                or x.show_without_published_products
            )
        )

        keep = QueryURL("/page/product_brands", brand_id=[])
        values = {"brand_rec": brand_rec, "keep": keep}
        if post.get("search"):
            values.update({"search": post.get("search")})
        return request.render("website_sale_product_brand.product_brands", values)
