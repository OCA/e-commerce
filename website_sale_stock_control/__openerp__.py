# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Stock Control",
    "summary": "Do not show products without stock in shop on line",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
        "stock",
    ],
    "data": [
        "views/templates.xml",
        "views/product_template_views.xml",
        "views/assets.xml",
    ],
}
