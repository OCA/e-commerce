# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers import main as website_sale_controller


class WebsiteSale(website_sale_controller.WebsiteSale):
    def checkout_values(self, **kw):
        values = super().checkout_values(**kw)
        order = values.get("order")
        partner = order.partner_id.sudo()
        commercial = partner.commercial_partner_id

        param = request.env["ir.config_parameter"].sudo()
        if param.get_param("website_sale.filter_child_shipping") == "True":
            if partner.id != commercial.id:
                values["shippings"] = values["shippings"].filtered_domain(
                    [
                        ("id", "child_of", partner.ids),
                        ("type", "in", ["delivery", "other"]),
                    ]
                )
                if order.partner_shipping_id.id not in values["shippings"].ids:
                    order.partner_shipping_id = partner

        return values

    def _express_disabled(self):
        return (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale.disable_express_checkout", "False")
            == "True"
        )

    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        if self._express_disabled():
            kw.pop("express", None)
        return super().cart_update(product_id, add_qty, set_qty, **kw)

    @http.route()
    def checkout(self, **post):
        if self._express_disabled():
            post.pop("express", None)
        return super().checkout(**post)
