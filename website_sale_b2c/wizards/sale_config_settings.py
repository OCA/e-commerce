# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    group_show_price_subtotal = fields.Boolean(
        "Show subtotal",
        implied_group='website_sale_b2c.group_show_price_subtotal',
        group='base.group_portal,base.group_user,base.group_public',
    )
    group_show_price_total = fields.Boolean(
        "Show total",
        implied_group='website_sale_b2c.group_show_price_total',
        group='base.group_portal,base.group_user,base.group_public',
    )
    sale_show_tax = fields.Selection(
        [('subtotal', 'Show line subtotals without taxes (B2B)'),
         ('total', 'Show line subtotals with taxes included (B2C)')],
        "Tax Display",
        default='subtotal',
        required=True,
    )

    @api.onchange('sale_show_tax')
    def _onchange_sale_tax(self):
        if self.sale_show_tax == "subtotal":
            self.update({
                'group_show_price_total': False,
                'group_show_price_subtotal': True,
            })
        else:
            self.update({
                'group_show_price_total': True,
                'group_show_price_subtotal': False,
            })

    @api.multi
    def set_sale_tax_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'sale_show_tax', self.sale_show_tax)
