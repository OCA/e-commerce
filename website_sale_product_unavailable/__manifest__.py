# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    'name': 'Unavailable Products',
    'summary': 'Adds notion of unavailable products visible in website shop',
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
        'static/src/xml/product_unavailable.xml',
    ],
    'demo': [
        'demo/product_product.xml',
    ]
}
