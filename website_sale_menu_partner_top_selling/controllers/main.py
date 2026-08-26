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
        param_limit = int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale_menu_partner_top_selling.limit", 10)
        )
        # Get best-selling products from the user
        partner = request.env.user.partner_id
        company_partner = partner.commercial_partner_id or partner
        product_data = (
            request.env["sale.order.line"]
            .sudo()
            ._read_group(
                domain=[
                    (
                        "order_id.partner_id.commercial_partner_id",
                        "=",
                        company_partner.id,
                    ),
                    ("order_id.state", "in", ["sale", "done"]),
                    ("product_id.product_tmpl_id.website_published", "=", True),
                    (
                        "product_id.product_tmpl_id.website_id",
                        "in",
                        [request.website.id, False],
                    ),
                    (
                        "product_id.product_tmpl_id.company_id",
                        "in",
                        [request.website.company_id.id, False],
                    ),
                ],
                groupby=["product_id"],
                aggregates=["product_uom_qty:sum"],
            )
        )
        # Sum quantities per template (a template may have several variants sold)
        template_quantities = {}
        for product, qty in product_data:
            template = product.product_tmpl_id
            template_quantities[template] = template_quantities.get(template, 0) + qty
        # Sort the templates by total quantity sold and limit
        sorted_templates = sorted(
            template_quantities, key=template_quantities.get, reverse=True
        )
        templates = request.env["product.template"].concat(
            *sorted_templates[:param_limit]
        )
        # Pagination
        ppg = website.shop_ppg or 21
        total_products = len(templates)
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
