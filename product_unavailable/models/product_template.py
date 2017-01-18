# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore, LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    availability = fields.Selection(
        selection_add=[('unavailable', 'Unavailable')],
    )
