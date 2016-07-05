# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    default_checkout_country_id = fields.Many2one(
        related='website_id.default_checkout_country_id',
        string='Default country for VAT codes')
