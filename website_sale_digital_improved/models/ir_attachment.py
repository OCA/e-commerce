# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models, tools


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    product_mailable = fields.Boolean(
        "Attach to invoice mail",
        help="Attach this digital product to the invoice. "
        "Enable only if you use instant payment methods exclusively.",
    )

    def _generate_download_checksum(self, timestamp):
        self.ensure_one()
        return tools.hmac(self.env, f"website_sale_digital-{self.id}", str(timestamp))
