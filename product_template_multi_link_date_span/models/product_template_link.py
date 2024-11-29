# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Thierry Ducrest <thierry.ducrest@camptocamp.com>
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models


class ProductTemplateLink(models.Model):
    _inherit = "product.template.link"

    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    limited_by_dates = fields.Boolean(related="type_id.limited_by_dates")
    mandatory_date_start = fields.Boolean(related="type_id.mandatory_date_start")

    @api.depends("date_start", "date_end", "type_id.limited_by_dates")
    def _compute_is_link_active(self):
        res = super()._compute_is_link_active()
        today = fields.Date.today()
        for record in self:
            if record.limited_by_dates:
                record.is_link_active = (
                    (record.date_start or today) <= today <= (record.date_end or today)
                )
        return res

    @api.constrains("type_id", "date_start")
    def _check_mandatory_date_start(self):
        for rec in self:
            if rec.mandatory_date_start and not rec.date_start:
                raise exceptions.UserError(
                    self.env._(
                        "A start date is required according to link type: %s",
                        rec.type_id.name,
                    )
                )
