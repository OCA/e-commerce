# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import models, fields


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    google_feed_expiry_time = fields.Integer(
        related=['website_id', 'google_feed_expiry_time'])

    google_image_size = fields.Integer(
        related=['website_id', 'google_image_size'])

    google_use_shipping_settings = fields.Boolean(
        related=['website_id', 'google_use_shipping_settings'])

    google_shipping_country = fields.Char(
        related=['website_id', 'google_shipping_country'])

    google_shipping_service = fields.Char(
        related=['website_id', 'google_shipping_service'])

    google_shipping_price = fields.Float(
        related=['website_id', 'google_shipping_price'])
