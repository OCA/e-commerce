# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sale Stock Force Block',
    'summary': 'Block sales for a product',
    'version': '12.0.1.0.0',
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
    'uninstall_hook': 'uninstall_hook',
}
