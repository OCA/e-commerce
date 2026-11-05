# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    exclude_from_website_stock = fields.Boolean(
        string="Exclude from Website Stock",
        default=False,
        help="If set, the on-hand quantity in this location is NOT counted "
        "towards the stock quantity displayed on the website shop. "
        "Only applies to internal locations.",
    )
