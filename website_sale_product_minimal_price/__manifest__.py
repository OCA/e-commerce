# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sale Product Minimal Price',
    'summary': 'Display minimal price for products that has variants',
    'version': '12.0.2.0.0',
    'development_status': 'Production/Stable',
    'maintainers': ['sergio-teruel'],
    'category': 'Website',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale_stock',
    ],
    'demo': [
        'demo/assets.xml',
    ],
    'data': [
        'views/assets.xml',
        'views/templates.xml',
    ],
}
