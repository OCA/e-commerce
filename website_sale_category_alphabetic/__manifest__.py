# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Website Sale - Alphabetic Categories',
    'summary': 'Automatically adds the correct alphabetic website category to'
               ' all new products',
    'version': '10.0.1.0.0',
    'category': 'Website',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'data/product_public_category.xml',
    ],
    'demo': [
        'demo/product_public_category.xml',
        'demo/product_template.xml',
    ],
    'post_init_hook': 'post_init_hook_categorize_existing_products',
}
