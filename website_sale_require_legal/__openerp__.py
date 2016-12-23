# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require accepting legal terms to checkout",
    "summary": "Force the user to accept legal tems to buy in the web shop",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "http://www.tecnativa.com",
    "author": "Antiun Ingeniería S.L., "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_legal_page",
        "website_sale",
    ],
    "data": [
        "views/website_sale.xml",
    ],
}
