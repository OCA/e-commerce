# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Website Sale Partner Type',
    'category': 'e-commerce',
    'author': "Odoo Community Association (OCA), "
              "Agile Business Group",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'website': 'http://www.agilebg.com',
    'depends': [
        'sale',
        'website_sale'
    ],
    'data': [
        'views/templates.xml',
        'views/assets.xml',
        'views/partner_view.xml',
    ],
    'installable': True,
}
