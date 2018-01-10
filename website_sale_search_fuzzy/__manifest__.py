# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "eCommerce Fuzzy Search",
    "summary": "Extends eCommerce with fuzzy searches for product names",
    "version": "10.0.1.0.0",
    "category": "eCommerce",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "post_init_hook": "_add_trgm_index_product_tmpl_name",
    "depends": [
        "website_sale",
        "base_search_fuzzy",
    ],
}
