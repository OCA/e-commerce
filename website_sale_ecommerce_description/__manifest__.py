# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website Sale e-Commerce Description',
    'category': 'Website',
    'summary': 'Add a e-Commerce description',
    'version': '11.0.1.0.1',
    'author': 'Okia SPRL, Odoo Community Association (OCA)',
    'depends': ['website_sale', 'product'],
    'license': 'AGPL-3',
    'data': [
        'views/website_sale_template.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'application': False,
}
