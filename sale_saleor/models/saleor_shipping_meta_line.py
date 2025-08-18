# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShippingMethodMetaLine(models.Model):
    _name = "shipping.method.meta.line"
    _description = "Shipping Method Metadata Line"
    _order = "id"

    carrier_id = fields.Many2one("delivery.carrier", required=True, ondelete="cascade")
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class ShippingMethodPrivateMetaLine(models.Model):
    _name = "shipping.method.private.meta.line"
    _description = "Shipping Method Private Metadata Line"
    _order = "id"

    carrier_id = fields.Many2one("delivery.carrier", required=True, ondelete="cascade")
    key = fields.Char(required=True)
    value = fields.Char(required=True)
