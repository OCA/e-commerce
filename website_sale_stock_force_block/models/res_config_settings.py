# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inventory_availability = fields.Selection(selection_add=[
        ('custom_block',
         'Block sales on website and display a message custom'),
    ])
