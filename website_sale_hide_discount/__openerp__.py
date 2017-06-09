# -*- coding: utf-8 -*-
# Copyright 2016-201 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Website Sale Product Hide Discount',
    'summary': 'Only show the pricelist price in website sale, without '
               'the original price or discount.',
    'version': '9.0.1.0.0',
    'category': 'Website',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'views/website_sale_template.xml',
    ],
}
