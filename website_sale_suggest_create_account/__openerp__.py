# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Suggest to create user account when buying",
    "summary": "Suggest users to create an account when buying in the website",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "http://www.antiun.com",
    "author": "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/website_sale.xml",
    ],
}
