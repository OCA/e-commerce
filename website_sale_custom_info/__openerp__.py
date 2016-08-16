# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Products Custom Information In Online Shop",
    "summary": "Display custom information in your online shop",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://tecnativa.com/",
    "author": "Tecnativa",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product_custom_info",
        "website_sale",
    ],
    "data": [
        "views/assets.xml",
        "views/custom_info_property_view.xml",
        "views/custom_info_template_view.xml",
        "views/product.xml",
        "views/search.xml",
    ],
}
