# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Website Sale Partner Type',
    'category': 'e-commerce',
    'author': "Agile Business Group,"
              "Odoo Community Association (OCA)",
    'version': '8.0.1.0.0',
    'website': 'http://www.agilebg.com',
    'depends': [
        'sale',
        'website_sale'
    ],
    'data': [
        'views/templates.xml',
        'views/assets.xml',
        'views/partner_view.xml'
    ],
    'installable': True,
}
