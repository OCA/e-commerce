# Copyright 2015-2017 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.http import request, route

from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _get_mandatory_billing_fields(self):
        result = super()._get_mandatory_billing_fields()
        return result + self._mandatory_legal_terms()

    def _get_mandatory_shipping_fields(self):
        result = super()._get_mandatory_shipping_fields()
        return result + self._mandatory_legal_terms()

    def _mandatory_legal_terms(self):
        """Require ``accepted_legal_terms`` only if we are validating."""
        result = []
        if request.context.get("needs_legal"):
            result.append("accepted_legal_terms")
        return result

    def checkout_form_validate(self, mode, all_form_values, data):
        """Require accepting legal terms to validate form."""
        # Patch context
        old_context = request.context
        request.context = dict(
            request.context,
            needs_legal=request.website.viewref(
                "website_sale_require_legal.address_require_legal"
            ).active,
        )
        result = super().checkout_form_validate(mode, all_form_values, data)
        # Unpatch context
        request.context = old_context
        return result

    def _checkout_form_save(self, mode, checkout, all_values):
        res = super()._checkout_form_save(mode, checkout, all_values)
        if all_values.get("submitted") and all_values.get("accepted_legal_terms"):
            partner = request.env["res.partner"].browse(res)
            self._log_acceptance_metadata(partner)
        return res

    def _log_acceptance_metadata(self, record):
        """Log legal terms acceptance metadata."""
        environ = request.httprequest.headers.environ
        message = _("Website legal terms acceptance metadata: %s")
        metadata = "<br/>".join(
            "{}: {}".format(val, environ.get(val))
            for val in ("REMOTE_ADDR", "HTTP_USER_AGENT", "HTTP_ACCEPT_LANGUAGE",)
        )
        record.sudo().message_post(body=message % metadata, message_type="notification")

    @route()
    def payment_transaction(
        self,
        acquirer_id,
        save_token=False,
        so_id=None,
        access_token=None,
        token=None,
        **kwargs
    ):
        """Record sale order payment legal terms acceptance.

        If the "Accept Terms & Conditions" upstream view is enabled in the
        website, to get here, user must have accepted legal terms.
        """
        result = super().payment_transaction(
            acquirer_id, save_token, so_id, access_token, token, **kwargs
        )
        # If the "Accept Terms & Conditions" view is disabled, we log nothing
        if not request.website.viewref("website_sale.payment_sale_note").active:
            return result
        # Retrieve the sale order
        if so_id:
            env = request.env["sale.order"]
            domain = [("id", "=", so_id)]
            if access_token:
                env = env.sudo()
                domain.append(("access_token", "=", access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()
        # Log metadata in the sale order
        if order:
            self._log_acceptance_metadata(order)
        return result
