# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Webshop Product Filter Extension",
    "version": "9.0.2.2.0",
    "author": "Odoo Community Association (OCA), Therp BV",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Adds 2 usefull booleans to fields for extended filtering",
    "depends": [
        'base',
        'webshop_product_filter',
        'product_category_attribute_set',
        'base_view_inheritance_extension',
    ],
    "data": [
        "views/extend_product_category_attribute_set.xml",
    ],
}
