# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    availability_sequence_dict = {
        'in_stock': 0,
        'warning': 5,
        'unavailable': 10,
        'empty': 20,
    }

    availability = fields.Selection(
        selection_add=[('unavailable', 'Unavailable')],
    )
    availability_sequence = fields.Integer(
        compute='_compute_availability_sequence',
        store=True,
    )

    @api.depends('availability')
    def _compute_availability_sequence(self):
        for r in self:
            r.availability_sequence = self.availability_sequence_dict.get(
                r.availability,
                20,
            )
