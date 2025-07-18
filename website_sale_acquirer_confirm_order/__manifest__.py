# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "eCommerce Confirm Order By Payment Acquirer",
    "summary": "eCommerce Confirm Order By Payment Acquirer",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "version": "14.0.1.0.0",
    "category": "Website/Website",
    "website": "https://github.com/OCA/e-commerce",
    "maintainers": ["pilarvargas-tecnativa"],
    "license": "AGPL-3",
    "depends": ["payment", "website_sale"],
    "data": [
        "views/assets.xml",
        "views/payment_acquirer.xml",
    ],
    "installable": True,
}
