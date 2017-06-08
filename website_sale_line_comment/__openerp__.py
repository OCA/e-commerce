# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website Sale Line Comment',
    "version": "9.0.1.0.0",
    'summary': 'Website Sale Line Comment',
    'description': """
    It Allows user to add notes in order line.
    """,
    'category': 'E-commerce',
    'website': 'http://www.serpentcs.com',
    "author": """Serpent Consulting Services Pvt. Ltd.,
                Agile Business Group,
                Odoo Community Association (OCA)""",
    "license": "AGPL-3",
    'depends': ['website_sale'],
    'data': [
        'views/sale_order.xml',
        'views/report_saleorder.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}