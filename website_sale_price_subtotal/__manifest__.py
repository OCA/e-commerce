# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore, LLC
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale - Price Subtotal",
    "summary": "Product page shows subtotal instead of unit price",
    "version": "10.0.1.0.0",
    "category": "E-Commerce",
    "website": "https://odoo-community.org/",
    "author": "SMDrugstore, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
        "website_sale",
    ],
    "data": [
        "views/website_sale_price_subtotal_view.xml",
    ]
}
