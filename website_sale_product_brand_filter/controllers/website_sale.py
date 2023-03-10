# Copyright 2020 Advitus MB
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import http
from odoo.http import request

from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale


class Website(WebsiteSale):
    def _get_search_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        domain = super(Website, self)._get_search_domain(
            search=search,
            category=category,
            attrib_values=attrib_values,
            search_in_description=search_in_description,
        )

        # add selected brands to product search domain
        brands_list = request.httprequest.args.getlist("brand")
        return self._update_domain(brands_list, domain)

    def _update_domain(self, brands_list, domain):
        selected_brand_ids = [int(brand) for brand in brands_list]
        if brands_list:
            for leaf in domain:
                if leaf[0] == "product_brand_id":
                    domain.remove(leaf)
            domain += [("product_brand_id", "in", selected_brand_ids)]
        return domain

    def _get_brands(self, domain):
        return (
            request.env["product.brand"]
            .search(domain)
            .filtered(lambda x: x.products_count > 0)
        )

    def _build_brands_list(
        self,
        selected_brand_ids,
        search=None,
        products=None,
        search_product=None,
        category=None,
    ):
        domain = []
        if not products:
            domain = [("id", "in", selected_brand_ids)]
        else:
            if search or category:
                domain = [("product_ids", "in", search_product.ids)]
        return self._get_brands(domain)

    def _get_search_domain_no_brands(
        self, search, category, attrib_values, search_in_description
    ):
        domain = super(Website, self)._get_search_domain(
            search=search,
            category=category,
            attrib_values=attrib_values,
            search_in_description=search_in_description,
        )

        return domain

    def _remove_extra_brands(self, brands, search_product, attrib_values):
        search_product_brands = search_product.mapped("product_brand_id")
        if attrib_values:
            brands = brands.filtered(lambda b: b.id in search_product_brands.ids)
        # sort brands by name
        return brands.sorted(key=lambda brand: brand.name)

    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        res = super(Website, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )

        # parse selected attributes
        attrib_list = request.httprequest.args.getlist("attrib")
        attrib_values = res.qcontext["attrib_values"]

        # get filtered products
        products = res.qcontext["products"]
        domain = self._get_search_domain_no_brands(
            search, category, attrib_values, search_in_description=False
        )
        search_product = request.env["product.template"].search(domain)

        # build brands list
        brands_list = request.httprequest.args.getlist("brand")
        selected_brand_ids = [int(brand) for brand in brands_list]
        brands = self._build_brands_list(
            selected_brand_ids, search, products, search_product, category
        )

        brands = self._remove_extra_brands(brands, search_product, attrib_values)
        # assign values for usage in qweb
        res.qcontext["brands"] = brands
        res.qcontext["selected_brand_ids"] = selected_brand_ids
        res.qcontext["attr_valid"] = (
            search_product.mapped("attribute_line_ids").mapped("value_ids").ids
        )
        # keep selected brands in URL
        keep = QueryURL(
            "/shop",
            category=category and int(category),
            search=search,
            attrib=attrib_list,
            order=post.get("order"),
            brand=brands_list,
        )
        res.qcontext["keep"] = keep

        return res
