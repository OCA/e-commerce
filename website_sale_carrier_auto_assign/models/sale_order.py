# Copyright 2026 ADHOC SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _is_auto_set_carrier_on_create(self):
        self.ensure_one()
        if self.website_id:
            return False
        return super()._is_auto_set_carrier_on_create()
