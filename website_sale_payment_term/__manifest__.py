# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "website_sale_payment_term",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "",
    "summary": "",
    "depends": [
        'website_sale',
        'payment',
    ],
    "data": [
        'views/payment_acquirer.xml',
    ],
    "installable": True,
    "application": False,
}
