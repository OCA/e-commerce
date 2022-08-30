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
        methods=["POST"],
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
                warehouse=current_website.warehouse_id.id,
                website_sale_stock_available=True,
            )
            .browse(product_template_ids)
        )
        for template in templates.filtered(lambda t: t.is_published):
            res.append(
                {
                    "id": template.id,
                    "virtual_available": template.virtual_available,
                    "virtual_available_formatted": request.env[
                        "ir.qweb.field.float"
                    ].value_to_html(
                        template.virtual_available,
                        {"decimal_precision": "Product Unit of Measure"},
                    ),
                    "inventory_availability": template.inventory_availability,
                    "available_threshold": template.available_threshold,
                    "custom_message": template.custom_message,
                    "type": template.type,
                    "uom_name": template.uom_name,
                }
            )
        return res
