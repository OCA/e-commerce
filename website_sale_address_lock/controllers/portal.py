# Copyright 2026 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

# Partner fields written by /my/account that stay untouched when locked
ADDRESS_FIELDS = ("street", "city", "zip", "state_id", "country_id")


class CustomerPortalAddressLock(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        commercial_partner = request.env.user.partner_id.commercial_partner_id
        values["website_address_lock"] = commercial_partner.website_address_lock
        return values

    @http.route()
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        if (
            post
            and request.httprequest.method == "POST"
            and partner.commercial_partner_id.website_address_lock
        ):
            # The form hides the address inputs, but the standard validation
            # still requires them: send the current values instead.
            post.update(
                {
                    "street": partner.street or "",
                    "city": partner.city or "",
                    "zipcode": partner.zip or "",
                    "state_id": str(partner.state_id.id or ""),
                    "country_id": str(partner.country_id.id or ""),
                }
            )
        return super().account(redirect=redirect, **post)

    def on_account_update(self, values, partner):
        res = super().on_account_update(values, partner)
        if partner.commercial_partner_id.website_address_lock:
            for fname in ADDRESS_FIELDS:
                values.pop(fname, None)
        return res
