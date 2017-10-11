# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website Sale Cart Selectable',
    'version': '10.0.1.1.0',
    'summary': 'Enables to control button Add to cart display per product',
    'author': 'OpenSynergy Indonesia, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://opensynergy-indonesia.com',
    'category': 'Website',
    'depends': ['website_sale'],
    'data': [
        'views/product_view.xml',
        'views/website_sale_template.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
