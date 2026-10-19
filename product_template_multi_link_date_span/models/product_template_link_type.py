# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateLinkType(models.Model):
    _inherit = "product.template.link.type"

    limited_by_dates = fields.Boolean(
        help="Links of this type will have a limited life based on start/end dates."
    )
    mandatory_date_start = fields.Boolean(
        help="When limited by dates, make date start required."
    )
