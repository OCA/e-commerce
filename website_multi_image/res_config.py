# coding: utf-8
from openerp import models, api


class WebsiteConfigSettings(models.TransientModel):

    _inherit = 'website.config.settings'

    @api.one
    def action_copy_shop_images(self):
        self.env['product.template'].search([]).action_copy_image_to_images()
