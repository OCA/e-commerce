# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import TableCompute, WebsiteSale


class WebsiteSaleRestrictPartnerProductController(WebsiteSale):
    def _get_portal_restricted_products(self, search_product, product_count):

        restrict_products_for_all_users = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "website_sale_restrict_by_pricelist.restrict_products",
                default="",
            )
        )
        if request.env.user.has_group("base.group_portal") and (
            request.env.user.restrict_products or bool(restrict_products_for_all_users)
        ):
            pricelist = request.env.user.property_product_pricelist
            if pricelist:
                products = pricelist.item_ids.mapped("product_tmpl_id")
                products = products.filtered(lambda p: p.is_published)
            else:
                products = request.env["product.template"].browse()
            return products, len(products)
        return (
            search_product,
            product_count,
        )

    @http.route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post,
    ):
        res = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post,
        )
        url = "/shop"
        if res.qcontext["category"]:
            url = "/shop/category/%s" % slug(res.qcontext["category"])
        (
            res.qcontext["search_product"],
            res.qcontext["product_count"],
        ) = self._get_portal_restricted_products(
            res.qcontext["search_product"], len(res.qcontext["search_product"])
        )
        res.qcontext["pager"] = request.website.pager(
            url=url,
            total=res.qcontext["product_count"],
            page=page,
            step=res.qcontext["ppg"],
            scope=5,
            url_args=post,
        )
        offset = res.qcontext["pager"]["offset"]
        res.qcontext["products"] = res.qcontext["search_product"][
            offset : offset + res.qcontext["ppg"]
        ]
        res.qcontext["bins"] = TableCompute().process(
            res.qcontext["products"], res.qcontext["ppg"], res.qcontext["ppr"]
        )
        return res
