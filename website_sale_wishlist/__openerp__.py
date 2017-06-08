# -*- coding: utf-8 -*-
# © 2016 Leonardo Donelli
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'E-commerce wishlist',
    'summary': 'User wishlist to collect the products he is interested in',
    'author': "MONK Software,Odoo Community Association (OCA)",
    'website': "http://www.wearemonk.com",
    'category': 'Website',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ['website_sale'],
    'data': [
        'templates/website.xml',
        'templates/website_sale.xml',
        'templates/website_sale_wishlist.xml',
        'security/ir.model.access.csv',
    ],
}
