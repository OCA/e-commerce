# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "eCommerce Checkout Comments",
    "summary": "Write comments in checkout process",
    "version": "8.0.1.0.0",
    "category": "Website",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        'views/template.xml',
    ]
}
