# Copyright 2026 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    website_address_lock = fields.Boolean(
        string="Lock Website Addresses",
        help="Contacts of this customer cannot add or edit addresses "
        "on the website or in the customer portal.",
    )

    def _can_be_edited_by_current_customer(self, sale_order, mode):
        return (
            super()._can_be_edited_by_current_customer(sale_order, mode)
            and not sale_order.partner_id.commercial_partner_id.website_address_lock
        )
