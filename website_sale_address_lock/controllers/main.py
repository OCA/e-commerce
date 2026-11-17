# Copyright 2026 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

# Fields a customer can still fill in from /my/account when addresses are locked
CONTACT_FIELDS = {"name", "email", "phone"}


class WebsiteSaleAddressLock(WebsiteSale):
    @http.route()
    def address(self, **kw):
        order = request.website.sale_get_order()
        if order.partner_id.commercial_partner_id.website_address_lock:
            if request.httprequest.method == "POST":
                raise Forbidden()
            return request.redirect("/shop/checkout")
        return super().address(**kw)

    def checkout_check_address(self, order):
        if not order.partner_id.commercial_partner_id.website_address_lock:
            return super().checkout_check_address(order)
        addresses = [
            (
                order.partner_invoice_id,
                self._check_billing_partner_mandatory_fields,
                self._get_mandatory_fields_billing,
            )
        ]
        if not order.only_services:
            addresses.append(
                (
                    order.partner_shipping_id,
                    self._check_shipping_partner_mandatory_fields,
                    self._get_mandatory_fields_shipping,
                )
            )
        for partner, is_complete, get_mandatory_fields in addresses:
            if is_complete(partner):
                continue
            missing_fields = {
                fname
                for fname in get_mandatory_fields(partner.country_id.id)
                if not partner[fname]
            }
            if (
                partner == request.env.user.partner_id
                and missing_fields <= CONTACT_FIELDS
            ):
                return request.redirect("/my/account?redirect=/shop/checkout")
            values = self.checkout_values(order)
            values["address_lock_incomplete"] = True
            return request.render("website_sale.checkout", values)
