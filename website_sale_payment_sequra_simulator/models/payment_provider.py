# Copyright 2025 Juan Carlos Oñate - Tecnativa <juancarlos.onate@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    sequra_asset_key = fields.Char(
        string="SeQura Asset Key",
        help="Asset Key provided by SeQura for the widget integration",
    )
    sequra_script_uri = fields.Char(
        string="SeQura Script URI",
        compute="_compute_sequra_script_uri",
        help="Script URI is automatically determined based on provider "
        "state (test/production)",
    )

    @api.depends("state")
    def _compute_sequra_script_uri(self):
        for provider in self:
            if provider.state == "test":
                provider.sequra_script_uri = (
                    "https://sandbox.sequracdn.com/assets/sequra-checkout.min.js"
                )
            else:
                provider.sequra_script_uri = (
                    "https://live.sequracdn.com/assets/sequra-checkout.min.js"
                )
