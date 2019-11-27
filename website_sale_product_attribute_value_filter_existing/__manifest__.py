# Copyright 2019 Tecnativa - Victor M.M. Torres
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Website Sale Attribute Value Existing',
    'summary': 'Allow hide attributes values not used in variants',
    'version': '12.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Website',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'views/assets.xml',
        'views/templates.xml',
    ],
}
