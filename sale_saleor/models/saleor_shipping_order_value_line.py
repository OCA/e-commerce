# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class OrderValueLine(models.Model):
    _name = "order.value.line"
    _description = "Order Value Line"
    _order = "id"

    channel_id = fields.Many2one(
        "saleor.channel",
        required=True,
        ondelete="restrict",
        help="Channel must be one of the channels assigned"
        " to the related shipping zones of this carrier.",
    )
    carrier_id = fields.Many2one("delivery.carrier", required=True, ondelete="cascade")
    display_unit = fields.Char(
        compute="_compute_display_unit", string="Unit", readonly=True
    )
    min_value = fields.Float()
    max_value = fields.Float()

    @api.depends("carrier_id")
    def _compute_display_unit(self):
        for line in self:
            if line.carrier_id.shipping_method_type == "price":
                currency = getattr(
                    getattr(line.carrier_id, "company_id", None), "currency_id", None
                )
                line.display_unit = currency.name if currency else ""
            elif line.carrier_id.shipping_method_type == "weight":
                line.display_unit = "KG"
            else:
                line.display_unit = ""
