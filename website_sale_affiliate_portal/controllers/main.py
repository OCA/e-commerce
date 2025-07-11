# Copyright 2020 Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal


class WebsiteAccount(CustomerPortal):
    @route()
    def account(self, **kw):
        """Add affiliation count to main account page"""
        response = super(WebsiteAccount, self).account(**kw)
        affiliate_model_sudo = request.env["sale.affiliate"].sudo()
        affiliate_count = affiliate_model_sudo.search_count(
            [
                ("partner_id", "=", request.env.user.partner_id.id),
            ]
        )
        response.qcontext.update(
            {
                "affiliate_count": affiliate_count,
            }
        )
        return response

    @route("/my/affiliations", type="http", auth="user", website=True)
    def affiliations(self):
        """Render a page to describe and display statistics about current
        partner's affiliations.
        """
        affiliate_model_sudo = request.env["sale.affiliate"].sudo()
        affiliates = affiliate_model_sudo.search(
            [
                ("partner_id", "=", request.env.user.partner_id.id),
            ]
        )
        values = self._prepare_portal_layout_values()
        values["affiliates"] = affiliates
        return request.render(
            "website_sale_affiliate_portal.portal_my_affiliations", values
        )
