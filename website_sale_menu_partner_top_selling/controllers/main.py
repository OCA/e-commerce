# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request
from odoo.tools import lazy

from odoo.addons.website_sale.controllers.main import TableCompute, WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route(
        ["/shop/my_regular_products", "/shop/my_regular_products/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
    )
    def user_regular_products(self, page=0, **kwargs):
        if request.env.user.has_group("base.group_public"):
            return request.redirect("/web/login")
        website = request.env["website"].get_current_website()
        templates = request.env.user.partner_id._get_my_regular_products(website)
        # Pagination
        total_products = len(templates)
        ppg = website.shop_ppg or 21
        page_count = (total_products + ppg - 1) // ppg
        page = max(0, min(page, page_count - 1))
        offset = page * ppg
        products_on_page = templates[offset : offset + ppg]
        pager = request.website.pager(
            url="/shop/my_regular_products",
            total=total_products,
            page=page + 1,
            step=ppg,
            scope=5,
            url_args=kwargs,
        )
        products_prices = lazy(lambda: products_on_page._get_sales_prices(website))
        # Map each product to its variant, like WebsiteSale.shop() does, since our
        # own product set differs from the one shop() computed for itself.
        variants = (
            request.env["product.product"]
            .sudo()
            .browse(
                product._get_first_possible_variant_id() for product in products_on_page
            )
        )
        variants.fetch()
        product_variants = dict(zip(products_on_page, variants, strict=False))
        # Shop context for the view
        shop_context = self.shop(page=page, **kwargs)
        shop_context.qcontext.update(
            {
                "pager": pager,
                "products": products_on_page,
                "search_product": products_on_page,
                "search_count": total_products,
                "product_variants": product_variants,
                "bins": lazy(
                    lambda: TableCompute().process(
                        products_on_page, ppg, website.shop_ppr or 4
                    )
                ),
                "products_prices": products_prices,
                "get_product_prices": lambda product: lazy(
                    lambda: products_prices[product.id]
                ),
            }
        )
        return request.render("website_sale.products", shop_context.qcontext)
