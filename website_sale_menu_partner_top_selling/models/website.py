# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_my_regular_products_menu_label(self):
        self.ensure_one()
        return self.company_id.regular_products_menu_label or self.env._(
            "My Regular Products"
        )
