# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Attribute sets on Product Category",
    "version": "9.0.2.0.1",
    "author": "Odoo Community Association (OCA), Therp BV",
    "license": "AGPL-3",
    "category": "Sales",
    "summary": """
    Extends Product category to have attribute for use in other modules
    """,
    "depends": [
        'sale',
        'ttr_product'
    ],
    "data": [
        'views/product_category.xml',
        'views/product_template.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
