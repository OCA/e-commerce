# Copyright 2015-2017 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from markupsafe import Markup

from odoo import http
from odoo.http import request, route

from odoo.addons.payment.controllers import portal
from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        is_main_address,
        **_kwargs,
    ):
        invalid_fields, missing_fields, error_messages = (
            super()._validate_address_values(
                address_values,
                partner_sudo,
                address_type,
                use_delivery_as_billing,
                required_fields,
                is_main_address,
                **_kwargs,
            )
        )
        if not _kwargs.get("accepted_legal_terms"):
            error_messages.append(
                request.env._("You must accept the terms & conditions to continue.")
            )

        return invalid_fields, missing_fields, error_messages

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
        res = super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            **form_data,
        )
        if partner_id:
            partner = request.env["res.partner"].browse(int(partner_id))
            if form_data.get("accepted_legal_terms"):
                self._log_acceptance_metadata(partner)
        return res

    def _log_acceptance_metadata(self, record):
        """Log legal terms acceptance metadata."""
        environ = request.httprequest.headers.environ
        metadata = "<br/>".join(
            f"{val}: {environ.get(val)}"
            for val in (
                "REMOTE_ADDR",
                "HTTP_USER_AGENT",
                "HTTP_ACCEPT_LANGUAGE",
            )
        )
        message = Markup(
            request.env._("Website legal terms acceptance metadata: %s") % metadata
        )
        record.sudo().message_post(
            body=message, message_type="notification", subtype_xmlid="mail.mt_comment"
        )


class PaymentPortal(portal.PaymentPortal):
    @http.route()
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """Record sale order payment legal terms acceptance.

        If the "Accept Terms & Conditions" upstream view is enabled in the
        website, to get here, user must have accepted legal terms.
        """
        result = super().shop_payment_transaction(order_id, access_token, **kwargs)
        # If the "Accept Terms & Conditions" view is disabled, we log nothing
        if not request.website.viewref(
            "website_sale.accept_terms_and_conditions"
        ).active:
            return result
        # Retrieve the sale order
        if order_id:
            sale_obj = request.env["sale.order"]
            domain = [("id", "=", order_id)]
            if access_token:
                sale_obj = sale_obj.sudo()
                domain.append(("access_token", "=", access_token))
            order = sale_obj.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()
        # Log metadata in the sale order
        if order:
            WebsiteSale._log_acceptance_metadata(self, order)
        return result
