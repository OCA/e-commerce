# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Syncronize internal categories and website categories",
    "version": "9.0.2.10.4",
    "author": "Therp BV",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "syncs all internal categories with website category",
    "depends": [
        'website_sale',
        'product_category_attribute_set',
        'webshop_product_filter',
        'product_multi_category',
        'website_sale_category_conditional',
    ],
    "data": [
        'wizards/product_to_category_wizard.xml',
        "views/product_product.xml",
        "data/ir_ui_view.xml",
    ],
    'post_init_hook': 'post_init_hook',
}
