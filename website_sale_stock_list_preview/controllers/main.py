# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.sale.controllers.variant import VariantController


class WebsiteSaleVariantController(VariantController):
    @http.route(
        ["/sale/get_combination_info_stock_preview"],
        type="json",
        auth="public",
        website=True,
    )
    def get_combination_info_stock_preview(self, product_template_ids, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        current_website = request.env["website"].get_current_website()
        res = []
        templates = (
            request.env["product.template"]
            .sudo()
            .with_context(
                warehouse=current_website.sudo().warehouse_id.id,
                website_sale_stock_available=True,
            )
            .browse(product_template_ids)
        )
        for template in templates.filtered(lambda t: t.is_published):
            variants = template.product_variant_ids
            res.append(
                {
                    "product_template": template.id,
                    "product_type": template.type,
                    "free_qty": sum(variants.mapped("free_qty")),
                    "cart_qty": sum(variants.mapped("cart_qty")),
                    "out_of_stock_message": template.out_of_stock_message,
                    "allow_out_of_stock_order": template.allow_out_of_stock_order,
                    "show_availability": template.show_availability,
                    "available_threshold": template.available_threshold,
                    "uom_name": template.uom_name,
                }
            )
        return res
