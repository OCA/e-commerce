# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Conditionally views categories on website",
    "version": "9.0.2.7.0",
    "author": "Odoo Community Association (OCA), Therp BV",
    "license": "AGPL-3",
    "category": "Website",
    "summary": """Conditionally views categories on websites and orders them in
                  the dropdown list by sequence number""",
    "depends": [
        'website_sale'
    ],
    "data": [
        "views/product_product.xml",
    ],
}
