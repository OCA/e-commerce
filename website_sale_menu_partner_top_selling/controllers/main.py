from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import TableCompute, WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route(
        ["/shop/my_regular_products", "/shop/my_regular_products/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
    )
    def user_regular_products(self, page=0, ppg=False, **kwargs):
        if request.env.user.has_group("base.group_public"):
            return request.redirect("/web/login")
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
            .read_group(
                [
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
                ["product_id", "product_uom_qty:sum"],
                ["product_id"],
                orderby="product_uom_qty DESC",
            )
        )
        top_product_ids = [
            rec["product_id"][0] for rec in product_data if rec["product_id"]
        ]
        # Search for templates of best-selling products
        product_templates = (
            request.env["product.product"]
            .sudo()
            .search([("id", "in", top_product_ids)])
        )
        template_quantities = {}
        for product in product_templates:
            template_id = product.product_tmpl_id.id
            if template_id not in template_quantities:
                template_quantities[template_id] = 0
            template_quantities[template_id] += next(
                rec["product_uom_qty"]
                for rec in product_data
                if rec["product_id"][0] == product.id
            )
        # Sort the templates by total quantity sold and limit
        sorted_template_ids = sorted(
            template_quantities.keys(),
            key=lambda tmpl_id: template_quantities[tmpl_id],
            reverse=True,
        )
        limited_template_ids = sorted_template_ids[:param_limit]
        templates = request.env["product.template"].sudo().browse(limited_template_ids)
        # Pagination
        ppg = ppg or 20
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
        # Shop context for the view
        shop_context = self.shop(page=page, ppg=ppg, **kwargs)
        shop_context.qcontext.update(
            {
                "pager": pager,
                "products": products_on_page,
                "search_product": products_on_page,
                "search_count": total_products,
                "bins": TableCompute().process(
                    products_on_page,
                    ppg,
                    request.env["website"].get_current_website().shop_ppr or 4,
                ),
            }
        )
        return request.render("website_sale.products", shop_context.qcontext)
