# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_name = fields.Char(
        string='Product name on website',
        help='Name to be shown on website,if not set normal name will be '
        'shown.'
    )
    display_website_name = fields.Char(
        compute='_compute_display_website_name', store=False
    )

    @api.multi
    @api.depends('name', 'website_name')
    def _compute_display_website_name(self):
        for this in self:
            this.display_website_name = this.website_name or this.name
