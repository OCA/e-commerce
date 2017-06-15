# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    'name': 'Website Sale - Price Subtotal',
    'summary': 'Show subtotals on product page instead of unit prices',
    'version': '10.0.1.0.0',
    'category': 'E-Commerce',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'templates/assets.xml',
    ],
    'demo': [
        'demo/product_attribute.xml',
        'demo/product_attribute_value.xml',
        'demo/product_product.xml',
        'demo/product_attribute_line.xml',
        'demo/product_pricelist_item.xml',
    ],
}
