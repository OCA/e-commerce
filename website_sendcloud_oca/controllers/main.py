# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.delivery import WebsiteSaleDelivery


class WebsiteSaleSendcloudDelivery(WebsiteSaleDelivery):
    def _update_website_sale_delivery_return(self, order, **post):
        res = super()._update_website_sale_delivery_return(order, **post)
        if order and post.get("carrier_id"):
            carrier_id = int(post["carrier_id"])
            carrier = request.env["delivery.carrier"].sudo().browse(carrier_id)
            if carrier and carrier.delivery_type == "sendcloud":
                res.update(order.sendcloud_sale_delivery_data(carrier))
        return res

    @http.route(
        ["/shop/sendcloud_update_service_point_address"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def sendcloud_update_service_point_address(self, **post):
        if post.get("order_id"):
            order = request.env["sale.order"].sudo().browse(post.get("order_id"))
            order.write(
                {
                    "sendcloud_service_point_address": post.get(
                        "sendcloud_service_point_address"
                    )
                }
            )
        return True
