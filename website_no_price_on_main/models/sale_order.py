# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_notes = fields.Text()
    from_website_id = fields.Many2one('website', string="Coming from website:")
    website_confirmed = fields.Boolean(
        string="Request for quotation sent",
        default=False
    )
