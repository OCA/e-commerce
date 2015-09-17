from openerp import api, models
from openerp.http import request


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_wishlist_items(self):
        return request.env['wishlist.item'].search([
            ('wishlist_id.user_id', '=', self.env.user.id)])
