# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json

from odoo import fields
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSaleForm


class WebsiteSaleForm(WebsiteSaleForm):
    @route(
        ["/shop/cart/update_json_from_shop"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def cart_update_json_from_shop(
        self,
        product_id=None,
        line_id=None,
        add_qty=None,
        set_qty=None,
        display=True,
        **kw
    ):

        # Needed for the test, because the test works in a different wat
        data = request.jsonrequest
        product_id = data.get("product_id") if not product_id else product_id
        line_id = data.get("line_id") if not line_id else line_id
        add_qty = data.get("add_qty", 1) if not add_qty else add_qty
        set_qty = data.get("set_qty", 0) if not set_qty else set_qty
        display = data.get("display") if data.get("display") is not None else display

        sale_order = request.website.sale_get_order(force_create=True)

        if sale_order.state != "draft":
            request.session["sale_order_id"] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get("product_custom_attribute_values"):
            product_custom_attribute_values = json.loads(
                kw.get("product_custom_attribute_values")
            )

        no_variant_attribute_values = None
        if kw.get("no_variant_attribute_values"):
            no_variant_attribute_values = json.loads(
                kw.get("no_variant_attribute_values")
            )

        value = sale_order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
        )
        value["cart_quantity"] = sale_order.cart_quantity
        if not sale_order.cart_quantity:
            request.website.sale_reset()
            return value

        if not display:
            return value

        value["website_sale.cart_lines"] = request.env["ir.ui.view"]._render_template(
            "website_sale.cart_lines",
            {
                "website_sale_order": sale_order,
                "date": fields.Date.today(),
                "suggested_products": sale_order._cart_accessories(),
            },
        )
        value["website_sale.short_cart_summary"] = request.env[
            "ir.ui.view"
        ]._render_template(
            "website_sale.short_cart_summary",
            {
                "website_sale_order": sale_order,
            },
        )

        order_line = (
            sale_order.sudo().order_line.filtered(
                lambda line: line.product_id.id == product_id
            )
            if sale_order and sale_order.order_line
            else []
        )

        value["product_cart_qty"] = (
            int(order_line[0].sudo().product_uom_qty)
            if order_line and order_line[0].product_uom_qty
            else 0
        )

        product = request.env["product.product"].sudo().browse(product_id)
        value["product_available_qty"] = product.qty_available - product.outgoing_qty

        return value

    # Controller needed for testing all lines
    @route("/set_sale_order_id", type="json", auth="public", methods=["POST"])
    def set_sale_order_id(self):
        data = request.jsonrequest
        sale_order_id = data.get("sale_order_id")
        request.session["sale_order_id"] = sale_order_id
        return {"status": "success", "message": "Sale order ID set in session"}
