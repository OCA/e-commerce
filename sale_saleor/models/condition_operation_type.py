# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ConditionOperationType(models.Model):
    _name = "condition.operation.type"
    _description = "Condition Operation Type"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    type = fields.Selection(
        selection=[
            ("catalogue", "Catalog"),
            ("order", "Order"),
        ]
    )
