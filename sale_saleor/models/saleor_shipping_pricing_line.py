# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShippingPricingLine(models.Model):
    _name = "shipping.pricing.line"
    _description = "Shipping Pricing Line"
    _order = "id"

    carrier_id = fields.Many2one("delivery.carrier", required=True, ondelete="cascade")
    price = fields.Float(required=True)
    channel_id = fields.Many2one("saleor.channel", required=True, ondelete="cascade")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="channel_id.currency_id",
        store=True,
        readonly=True,
    )
