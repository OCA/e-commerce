# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Affiliate Program",
    "summary": "Create an e-commerce affiliate program for the tracking of "
               "referrals and conversions.",
    "version": "10.0.1.0.1",
    "category": "E-Commerce",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "data/sale_affiliate_data.xml",
        "security/ir.model.access.csv",
        "views/sale_affiliate_view.xml",
        "views/sale_affiliate_request_view.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [
        "demo/sale_affiliate_demo.xml",
    ],
}
