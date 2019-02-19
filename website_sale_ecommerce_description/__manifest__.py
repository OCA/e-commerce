# -*- coding: utf-8 -*-
# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website Sale e-Commerce Description',
    'category': 'Website',
    'summary': 'Add a e-Commerce description',
    'version': '11.0.1.0.1',
    'description': """
The sale description is used in the e-commerce and also in other reports likes
invoices, sale orders, ....
In some case, we only need a description on the e-commerce. This module
will add a field description only for the e-commerce.
    """,
    'author': 'Okia SPRL, Odoo Community Association (OCA)',
    'depends': ['website_sale', 'product'],
    'data': [
        'views/website_sale_template.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'application': False,
}
