# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore, LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Unavailable",
    "summary": "Shows that a product is unavailable",
    "version": "10.0.1.0.0",
    "category": "E-Commerce",
    "website": "https://github.com/OCA/e-commerce/",
    "author": "SMDrugstore, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "demo/product_unavailable_demo.xml",
        "views/product_unavailable_view.xml",
    ],
}
