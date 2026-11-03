# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request
from odoo.tools.mail import is_html_empty

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStockListPreview(WebsiteSale):
    def _get_additional_shop_values(self, values, **kwargs):
        res = super()._get_additional_shop_values(values, **kwargs)

        products = values.get("products") or request.env["product.template"]
        if not products:
            return res

        website = values.get("website") or request.env["website"].search([], limit=1)
        products_sudo = products.sudo().with_context(
            warehouse=website.sudo().warehouse_id.id,
        )
        products_stock = {}
        for tmpl in products_sudo:
            out_msg = (
                False
                if is_html_empty(tmpl.out_of_stock_message)
                else tmpl.out_of_stock_message
            )
            if (
                not tmpl.show_availability
                and tmpl.allow_out_of_stock_order
                and not out_msg
            ):
                continue

            variants = tmpl.product_variant_ids
            products_stock[tmpl.id] = {
                "product_template": tmpl.id,
                "free_qty": sum(variants.mapped("free_qty")),
                "out_of_stock_message": out_msg,
                "allow_out_of_stock_order": tmpl.allow_out_of_stock_order,
                "show_availability": tmpl.show_availability,
                "available_threshold": tmpl.available_threshold,
                "uom_name": tmpl.uom_name,
                "uom_rounding": getattr(tmpl.uom_id, "rounding", 0.01),
            }
        res["products_stock"] = products_stock
        return res
