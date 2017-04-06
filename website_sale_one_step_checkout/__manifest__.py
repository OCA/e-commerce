# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'One Step Checkout',
    'category': 'e-commerce',
    'summary': 'Add OSC in your e-commerce shop',
    'version': '10.0.1.0.0',
    'author': 'bloopark systems GmbH & Co. KG,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.bloopark.de',
    'license': 'AGPL-3',
    'depends': [
        'website_sale'
    ],
    'data': [
        'views/res_config.xml',
        'views/website_sale_one_step_checkout.xml',
    ],
    'installable': True,
    'auto_install': False,
}
