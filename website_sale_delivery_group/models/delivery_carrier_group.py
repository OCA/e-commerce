from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    group_id = fields.Many2one(
        "delivery.carrier.group",
        help="Used to group shipping methods on the website checkout page",
    )


class DeliveryCarrierGroup(models.Model):
    _name = "delivery.carrier.group"
    _description = "Delivery Carrier Group"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    description = fields.Text()
    carrier_ids = fields.One2many(
        "delivery.carrier",
        "group_id",
        string="Carriers",
        readonly=True,
    )
