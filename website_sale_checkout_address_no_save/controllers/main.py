# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request, route

from odoo.addons.payment.controllers import post_processing
from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    @route(
        "/shop/address/submit",
        type="http",
        methods=["POST"],
        auth="public",
        website=True,
        sitemap=False,
    )
    def shop_address_submit(
        self,
        partner_id=None,
        address_type="billing",
        use_delivery_as_billing=None,
        callback=None,
        required_fields=None,
        **form_data,
    ):
        order = request.website.sale_get_order()
        parent_partner = order.partner_id
        Partner = request.env["res.partner"].sudo().with_context(active_test=False)
        domain = [
            ("active", "=", False),
            ("parent_id", "=", parent_partner.id),
            ("type", "=", "other"),
        ]
        if form_data.get("email"):
            domain.append(("email", "=", form_data["email"]))
        if form_data.get("phone"):
            domain.append(("phone", "=", form_data["phone"]))
        if form_data.get("street") and form_data.get("zip"):
            domain += [
                ("street", "ilike", form_data.get("street")),
                ("zip", "=", form_data.get("zip")),
            ]
        archived_child = Partner.search(domain, limit=1)
        if archived_child:
            archived_child.write({"active": True, **form_data})
            partner_id = archived_child.id
        if form_data.get("archive_address"):
            request.session["archive_address"] = True
        return super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            **form_data,
        )


class PaymentPostProcessing(post_processing.PaymentPostProcessing):
    @http.route(
        "/payment/status", type="http", auth="public", website=True, sitemap=False
    )
    def display_status(self, **kwargs):
        result = super().display_status(**kwargs)
        archive_address = request.session.pop("archive_address", False)
        if archive_address:
            sale_order_id = request.session.get("sale_last_order_id")
            if sale_order_id:
                order = request.env["sale.order"].sudo().browse(sale_order_id)
                order.partner_shipping_id.active = False
        return result
