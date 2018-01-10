# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    'name': 'Website Sale - Quantity Parameter',
    'summary': 'Support "quantity" URL parameter on shop product pages',
    'version': '10.0.1.0.0',
    'category': 'E-commerce',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'static/src/xml/website_sale_select_qty.xml',
    ],
}
