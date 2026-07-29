# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.fields import Domain


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(
        selection_add=[("one_time_delivery", "One-Time Delivery Address")],
        ondelete={"one_time_delivery": "set default"},
    )
    allow_dropship = fields.Boolean(
        string="Allow Drop-shipping",
        help=(
            "When enabled, this customer can use the one-time delivery flow "
            "during the website checkout: the delivery address is stored as a "
            "temporary 'one_time_delivery' contact while billing stays on the "
            "customer. The one-time delivery option is hidden for customers "
            "that do not allow drop-shipping."
        ),
    )

    def _get_delivery_address_domain(self):
        # Extend the delivery address domain to also list one_time_delivery
        # contacts alongside the standard 'delivery'/'other' addresses.
        res = super()._get_delivery_address_domain()
        if all(partner.allow_dropship for partner in self):
            res |= Domain(
                [
                    ("commercial_partner_id", "in", self.commercial_partner_id.ids),
                    ("type", "=", "one_time_delivery"),
                ]
            )
        return res
