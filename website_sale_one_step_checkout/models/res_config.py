# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'
    use_osc = fields.Boolean(
        related='website_id.use_osc',
        string='Use OSC')


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    @api.multi
    def write(self, vals):
        """Add or remove sale settings.

        Different shipping address for portal and public users.
        """
        setting = []

        group_shipping = self.env['ir.model.data'].xmlid_to_res_id(
            'sale.group_delivery_invoice_address')
        if 'group_sale_delivery_address' in vals:
            if vals['group_sale_delivery_address']:
                setting.append((4, group_shipping))
            else:
                setting.append((3, group_shipping))

        portal_group = self.env['ir.model.data'].xmlid_to_res_id(
            'base.group_portal')
        users = self.env['res.users'].search([('groups_id', '=',
                                               portal_group)])

        if users:
            users.write({'groups_id': setting})

        public_user = self.env.ref('base.public_user')

        if public_user:
            public_user.write({'groups_id': setting})

        return super(SaleConfiguration, self).write(vals)
