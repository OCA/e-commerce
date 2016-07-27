# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website Sale By Supplier',
    'version': '8.0.1.0.0',
    'summary': 'Publish Your Suppliers Products',
    'author': 'OpenSynergy Indonesia,Odoo Community Association (OCA)',
    'website': 'https://opensynergy-indonesia.com',
    'category': 'Website',
    'depends': [
        'website_supplier_list',
        'website_sale'
    ],
    'data': ['views/website_sale_by_supplier.xml'],
    'installable': True,
}
