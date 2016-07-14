# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import models, fields


class Website(models.Model):
    _inherit = 'website'

    google_feed_expiry_time = fields.Integer(
        string='Feed expiry time',
        help='Time to keep cached the feed. Set 0 hours to disable cache.',
        default=24)

    google_image_size = fields.Integer(
        string='Image size',
        help='Recomended square images of 800x800 pixels size. The minimum '
             'will be 100x100 and 250x250 for apparels.',
        default=800)

    google_use_shipping_settings = fields.Boolean(
        string='Use shipping settings',
        help='Uncheck this box if you prefer to use the Google Merchant '
             'Center shipping settings.',
        default=True)

    google_shipping_country = fields.Char(
        string='Shipping country',
        help='Product destination country code '
             '(such as ISO 3166 country code).')

    google_shipping_service = fields.Char(
        string='Shipping service',
        help='Shipping service description.',
        default='Standard')

    google_shipping_price = fields.Float(
        string='Shipping price',
        help='Fixed shipping price taxes included.')
