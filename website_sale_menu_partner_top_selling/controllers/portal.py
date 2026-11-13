# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request
from odoo.tools import str2bool

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        website = (
            getattr(request, "website", None)
            or request.env["website"].get_current_website()
        )
        values["my_regular_products_card_enabled"] = str2bool(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale_menu_partner_top_selling.portal_card"),
            False,
        )
        if not values["my_regular_products_card_enabled"]:
            return values
        values["my_regular_products_label"] = (
            website._get_my_regular_products_menu_label()
        )
        if "my_regular_products_count" in counters:
            values["my_regular_products_count"] = len(
                request.env.user.partner_id._get_my_regular_products(website)
            )
        return values
