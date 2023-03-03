# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    google_tag_manager_enhanced_conversions = fields.Boolean(
        string="Enhanced Conversions",
        help="This will provide the necessary data in the confirmation page that GTM "
        "needs to gather in order to be able to use Enhanced Conversions. The "
        "template can be edited if more info is needed in the future.",
    )
