# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Website Sale Search No Kept',
    'summary': 'Allow to delete search content when navigate to other '
               'category',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Website',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'maintainers': ['sergio-teruel'],
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'views/assets.xml',
    ],
}
