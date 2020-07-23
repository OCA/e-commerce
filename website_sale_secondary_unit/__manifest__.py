# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sale Secondary Unit',
    'summary': 'Allow manage secondary units in website shop',
    'version': '12.0.1.1.0',
    'development_status': 'Beta',
    'category': 'Website',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
        'sale_order_secondary_unit',
    ],
    'data': [
        'security/website_sale_secondary_unit.xml',
        'views/assets.xml',
        'views/product_template_views.xml',
        'views/product_secondary_unit_views.xml',
        'views/templates.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
