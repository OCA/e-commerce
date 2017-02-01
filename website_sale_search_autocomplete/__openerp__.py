# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Website Sale Search Autocomplete",
    "summary": "It provides autocomplete for E-Commerce search",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "website_field_autocomplete",
        "website_sale",
    ],
    "data": [
        "templates/website_template.xml",
    ],
}
