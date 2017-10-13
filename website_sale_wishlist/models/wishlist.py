# -*- coding: utf-8 -*-
# © 2016 Leonardo Donelli
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, fields, models


class ShopWishList(models.Model):
    _name = 'wishlist'

    user_id = fields.Many2one('res.users')
    item_ids = fields.One2many('wishlist.item', 'wishlist_id', string='Items')

    @api.multi
    def add_product(self, product_id):
        self.ensure_one()
        if product_id in self.item_ids.mapped('product_id.id'):
            return False  # already in wish list
        self.item_ids.create(
            {'wishlist_id': self.id, 'product_id': product_id})
        return True

    @api.multi
    def remove_product(self, product_id):
        self.ensure_one()
        item = self.item_ids.filtered(lambda x: x.product_id.id == product_id)
        if item:
            item.unlink()
            return True
        return False


class WishlistItem(models.Model):
    _name = 'wishlist.item'

    wishlist_id = fields.Many2one(
        'wishlist', ondelete='cascade', required=True)
    product_id = fields.Many2one(
        'product.product', ondelete='cascade', required=True)
    date_added = fields.Date('Date added', default=fields.Date.today)
