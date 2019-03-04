# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.http import request


class Website(models.Model):
    _inherit = 'website'

    is_main = fields.Boolean(
        string='Is main Website',
        default=False,
    )

    @api.multi
    def sale_get_order(
            self, force_create=False, code=None,
            update_pricelist=False, force_pricelist=False, context=None):
        # TODO understand why the signature had to have context explicitly in
        # order to fix an error raised in website_sale/controllers/main.py:L655
        res = super(Website, self).sale_get_order(
            force_create=force_create, code=code,
            update_pricelist=update_pricelist, force_pricelist=force_pricelist,
            context=context
        )
        if res:
            res.write({'from_website_id': request.website.id})
        return res
