# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_blacklist_warning = fields.Text(
        compute="_compute_partner_blacklist_warning",
        help="warning message",
        string="warning",
    )

    @api.depends("partner_id", "partner_id.blacklist")
    def _compute_partner_blacklist_warning(self):
        for rec in self:
            if rec.partner_id.blacklist:
                rec.partner_blacklist_warning = (
                    _("%s is marked as blacklisted") % rec.partner_id.name
                )
            else:
                rec.partner_blacklist_warning = ""
