# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Website Quote - Payment Messages',
    'summary': 'It adds the payment acquirer messages to website quotes.',
    'version': '10.0.1.0.0',
    'category': 'Website',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'payment',
        'website_quote',
    ],
    'data': [
        'templates/website_quote_template.xml',
    ],
}
