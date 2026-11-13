# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request
from odoo.tools import str2bool

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
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
        if values["my_regular_products_card_enabled"]:
            values["my_regular_products_label"] = (
                website._get_my_regular_products_menu_label()
            )
            values["my_regular_products_card_text"] = (
                website._get_my_regular_products_card_text()
            )
            values["my_regular_products_card_position"] = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "website_sale_menu_partner_top_selling.portal_card_position",
                    "top",
                )
            )
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "my_regular_products_count" not in counters:
            return values
        card_enabled = str2bool(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale_menu_partner_top_selling.portal_card"),
            False,
        )
        if not card_enabled:
            return values
        website = (
            getattr(request, "website", None)
            or request.env["website"].get_current_website()
        )
        # The badge counts products a customer can actually buy again, so
        # unpublished products are excluded even for internal users who can
        # preview them on the page itself.
        templates = request.env.user.partner_id._get_my_regular_products(website)
        values["my_regular_products_count"] = len(templates.filtered("is_published"))
        return values
