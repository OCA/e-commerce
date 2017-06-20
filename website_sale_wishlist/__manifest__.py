# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Products Wishlist",
    "summary": "Wishlist of products in your online shop",
    "version": "10.0.1.0.0",
    "category": "Website",
    "website": "https://tecnativa.com/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "demo": [
        "demo/assets.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "data/ir_cron.yml",
        "views/assets.xml",
        "views/layout.xml",
        "views/shop.xml",
    ],
}
