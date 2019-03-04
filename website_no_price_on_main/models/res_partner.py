# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.http import request


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_last_website_so_id_multiwebsite(self):
        for this in self:
            if not request or not request.website:
                this.last_website_so_id = this.env['sale.order']
                return
        curr_website = request.website
        for this in self:
            this.last_website_so_id = this.env['sale.order'].search(
                [('from_website_id', '=', curr_website.id),
                 ('state', '=', 'draft'),
                 ('create_uid', '=', this.env.uid),
                 ('website_confirmed', '=', False)],
                order="write_date desc", limit=1
            )

    last_website_so_id = fields.Many2one(
        compute=_compute_last_website_so_id_multiwebsite,
        store=False)
