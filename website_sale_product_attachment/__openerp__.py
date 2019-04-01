# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Attachments",
    "version": "9.0.1.0.0",
    "author": "Therp BV,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Add attachments to products and show them on the website",
    "depends": [
        'website_sale'
    ],
    "data": [
        'views/attachements_view.xml',
        'views/product_attachment.xml',
    ],
    "installable": True,
}
