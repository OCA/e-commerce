# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleProductDocumentVariantController(WebsiteSaleVariantController):
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
        variant = request.env["product.product"].browse(
            combination_info.get("product_id")
        )
        combination_info["product_documents_html"] = (
            product_template._get_variant_documents_html(variant)
        )
        return combination_info
