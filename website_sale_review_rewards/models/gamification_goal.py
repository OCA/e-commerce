# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import models


class ResPartner(models.Model):
    _inherit = "gamification.goal"

    def auto_update_goals(self):
        records = self.env[self._name].search(
            [("state", "=", "inprogress")],
        )
        for rec in records:
            today = datetime.date.today()
            start_date = rec.challenge_id.start_date
            end_date = rec.challenge_id.end_date
            if start_date and end_date:
                if today <= end_date:
                    rec.update_goal()
            else:
                rec.update_goal()
