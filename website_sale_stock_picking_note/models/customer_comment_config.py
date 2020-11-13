# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class Website(models.Model):

    """Adds the fields for options of the Custom Delivery Comment."""

    _inherit = "website"

    is_picking_note_feature = fields.Boolean(
        string="Disable custom delivery comment feature"
    )


class ResConfigSettings(models.TransientModel):

    """Settings for the Custom Delivery Comment."""

    _inherit = "res.config.settings"

    is_picking_note_feature = fields.Boolean(
        related="website_id.is_picking_note_feature",
        string="Disable custom delivery comment feature",
        readonly=False,
    )
