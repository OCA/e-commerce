# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models


class WebsiteConfigSettings(models.TransientModel):

    _inherit = "website.config.settings"

    is_main = fields.Boolean(
        related='website_id.is_main',
    )
