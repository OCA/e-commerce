# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_ecommerce = fields.Text(
        'e-Commerce description',
        help='A description of the Product. This description will be displayed'
             ' only on your e-Commerce.'
    )
