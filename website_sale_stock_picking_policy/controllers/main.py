# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSalePickingPolicy(WebsiteSale):
    def _prepare_checkout_page_values(self, order_sudo, **kwargs):
        # Prepare checkout page values including picking policy selection.
        result = super()._prepare_checkout_page_values(order_sudo, **kwargs)

        picking_policy_selection = dict(
            order_sudo._fields["picking_policy"]._description_selection(request.env)
        )

        result.update(
            {
                "picking_policy_selection_values": picking_policy_selection,
            }
        )

        return result

    @route(
        "/shop/update_picking_policy",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def update_picking_policy(self, picking_policy, **kwargs):
        """Update the picking policy field on the current cart."""

        order = request.cart
        if not order:
            raise UserError(request.env._("No active cart found."))

        order.write({"picking_policy": picking_policy})

        result = {}
        if order.expected_date:
            result["expected_date"] = fields.Date.to_string(
                fields.Date.context_today(order, order.expected_date)
            )
        else:
            result["expected_date"] = False

        return result
