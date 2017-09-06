# -*- coding: utf-8 -*-
# Copyright 2015, 2017 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require accepting legal terms to checkout",
    "summary": "Force the user to accept legal tems to buy in the web shop",
    "version": "10.0.1.0.0",
    "category": "Website",
    "website": "https://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web_tour",
        "website_legal_page",
        "website_sale",
    ],
    "data": [
        "views/website_sale.xml",
    ],
    "demo": [
        "demo/assets.xml",
    ],
}
