# © 2020 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Website Sale Product Description',
    'category': 'Website',
    'summary': 'Shows custom e-Commerce description for products',
    'version': '12.0.1.0.0',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Solvos, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['website_sale'],
    'data': [
        'views/website_sale_template.xml',
        'views/product_template.xml',
    ],
    'demo': [
        'data/demo_website_sale_product_description.xml',
    ],
}
