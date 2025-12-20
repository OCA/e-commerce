# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStockListPreview(WebsiteSale):
    def _get_additional_shop_values(self, values):
        res = super()._get_additional_shop_values(values)

        products = values.get("products") or request.env["product.template"]
        if not products:
            return res
        website = request.env["website"].get_current_website()
        products_sudo = products.sudo().with_context(
            warehouse=website.sudo().warehouse_id.id,
            website_sale_stock_available=True,
        )
        products_stock = {}
        for tmpl in products_sudo:
            if not tmpl.show_availability:
                continue
            variants = tmpl.product_variant_ids
            products_stock[tmpl.id] = {
                "product_template": tmpl.id,
                "product_type": tmpl.type,
                "free_qty": sum(variants.mapped("free_qty")),
                "out_of_stock_message": tmpl.out_of_stock_message,
                "allow_out_of_stock_order": tmpl.allow_out_of_stock_order,
                "show_availability": tmpl.show_availability,
                "available_threshold": tmpl.available_threshold,
                "uom_name": tmpl.uom_name,
                "uom_rounding": tmpl.uom_id.rounding,
            }
        res["products_stock"] = products_stock
        return res
