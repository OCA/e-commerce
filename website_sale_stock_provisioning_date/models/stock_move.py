# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from pytz import timezone

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    date_provisioning = fields.Date(
        string="Date expected", compute="_compute_date_provisioning", store=True,
    )

    @api.depends("date_expected")
    def _compute_date_provisioning(self):
        """We want to store the date in the context of the user that sets it avoiding
        offsets due to timezones. This way, when it's shown in the website, we can
        ensure that it's our date and not the user's"""
        self.date_provisioning = False
        tz = timezone(self.env.user.tz or "UTC")
        for move in self.filtered("date_expected"):
            move.date_provisioning = move.date_expected.astimezone(tz).date()
