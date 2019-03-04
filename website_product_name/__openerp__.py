# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Name",
    "version": "9.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Shows a different name for the product on website",
    'website': 'https://github.com/OCA/e-commerce',
    "depends": [
        'website_sale',
    ],
    "data": [
        "views/views.xml",
        'views/templates.xml',
    ],
}
