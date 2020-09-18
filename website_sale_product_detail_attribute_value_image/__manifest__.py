# Copyright 2019 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sale Product Detail Attribute Value Image',
    'summary': 'Display attributes values images in shop product detail',
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
    ],
    'data': [
        'views/product_attribute_value_views.xml',
        'templates/assets.xml',
        'templates/shop_product.xml',
    ],
    'demo': [
        'demo/assets_tour.xml',
    ],
}
