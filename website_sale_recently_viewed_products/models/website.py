from odoo import api, models
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def recently_viewed_products(self):
        return request.env['website.sale.product.view'].search([
            ('sessionid', '=', request.session.sid)], limit=10)
