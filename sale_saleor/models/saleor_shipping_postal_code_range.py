# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PostalCodeRange(models.Model):
    _name = "postal.code.range"
    _description = "Postal Code Range"
    _order = "id"

    carrier_id = fields.Many2one("delivery.carrier", required=True, ondelete="cascade")
    start_zip = fields.Char(string="Postal Code Start", required=True)
    end_zip = fields.Char(string="Postal Code End", required=True)
