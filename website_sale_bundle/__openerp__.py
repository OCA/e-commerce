# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Product Bundles in Shop",
    "summary": "Allow you to sell online product bundles",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://tecnativa.com/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "auto_install": True,
    "images": [
        "static/description/website_bundle.png",
        "static/description/optional_templates.png",
    ],
    "depends": [
        "product_bundle",
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "views/templates.xml",
        "views/cart.xml",
        "views/shop_product.xml",
    ],
}
