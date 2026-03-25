# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    cart_import_button = fields.Boolean(string="Is the cart import button enabled?")
    cart_import_button_file_limit = fields.Float(
        string="Cart import button file size limit (MB)", default=2
    )

    _sql_constraints = [
        (
            "cart_import_button_file_limit_min",
            "CHECK (cart_import_button_file_limit > 0)",
            "The file size limit must be positive",
        ),
    ]
