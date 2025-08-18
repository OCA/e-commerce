# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShippingZoneMetaLine(models.Model):
    _name = "shipping.zone.meta.line"
    _description = "Shipping Zone Metadata Line"
    _order = "id"

    zone_id = fields.Many2one("saleor.shipping.zone", required=True, ondelete="cascade")
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class ShippingZonePrivateMetaLine(models.Model):
    _name = "shipping.zone.private.meta.line"
    _description = "Shipping Zone Private Metadata Line"
    _order = "id"

    zone_id = fields.Many2one("saleor.shipping.zone", required=True, ondelete="cascade")
    key = fields.Char(required=True)
    value = fields.Char(required=True)
