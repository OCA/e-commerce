# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    one_time_delivery = fields.Boolean(
        string="One-Time Delivery Address",
        help=(
            "When enabled, the delivery address created during the website "
            "checkout is stored as a temporary contact with type "
            "'one_time_delivery' instead of the standard 'delivery' type. "
            "This keeps the recipient out of the customer's regular address "
            "book and is useful for reseller orders shipped to an end customer."
        ),
    )
    allow_dropship = fields.Boolean(
        related="partner_id.commercial_partner_id.allow_dropship",
    )

    def action_confirm(self):
        """Archive one-time delivery contacts once the order is confirmed.

        A one_time_delivery contact is a temporary recipient that is no longer
        needed for editing once the order is placed. Archiving (not deleting)
        keeps it out of the address book while remaining readable on the
        related pickings and order history.
        """
        res = super().action_confirm()
        one_time_partners = self.partner_shipping_id.filtered(
            lambda partner: partner.type == "one_time_delivery"
        )
        if one_time_partners:
            one_time_partners.action_archive()
        return res
