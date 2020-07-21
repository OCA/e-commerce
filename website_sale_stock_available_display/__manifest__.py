# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sale Stock Available Display',
    'summary': 'Display stock in shop online and allow to sell with no stock '
               'available',
    'version': '12.0.1.2.1',
    'development_status': 'Beta',
    'category': 'Website',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale_stock',
    ],
    'data': [
        'views/assets.xml',
        'views/product_template_views.xml',
        'views/templates.xml',
    ],
}
