# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplateLink(models.Model):

    _inherit = "product.template.link"

    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    is_link_active = fields.Boolean(compute="_compute_is_link_active")

    @api.depends("date_start", "date_end")
    def _compute_is_link_active(self):
        today = fields.Date.today()
        for record in self:
            record.is_link_active = (
                (record.date_start or today) <= today <= (record.date_end or today)
            )
