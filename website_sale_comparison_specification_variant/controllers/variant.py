# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleSpecificationExclusionVariantController(WebsiteSaleVariantController):
    @route(
        "/website_sale/get_combination_info",
        type="jsonrpc",
        auth="public",
        methods=["POST"],
        website=True,
        readonly=True,
    )
    def get_combination_info_website(
        self,
        product_template_id,
        product_id,
        combination,
        add_qty,
        uom_id=None,
        **kwargs,
    ):
        combination_info = super().get_combination_info_website(
            product_template_id=product_template_id,
            product_id=product_id,
            combination=combination,
            add_qty=add_qty,
            uom_id=uom_id,
            **kwargs,
        )
        product_template = request.env["product.template"].browse(
            int(product_template_id)
        )
        combination_values = request.env["product.template.attribute.value"].browse(
            combination
        )
        specs_table_html = product_template._get_specs_table_html(combination_values)
        if specs_table_html is not None:
            combination_info["specs_table_html"] = specs_table_html
        specs_accordion_html = product_template._get_specs_accordion_html(
            combination_values
        )
        if specs_accordion_html is not None:
            combination_info["specs_accordion_html"] = specs_accordion_html
        return combination_info
