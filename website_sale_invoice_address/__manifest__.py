# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Invoice Address",
    "summary": "Set e-Commerce sale orders invoice address as in backend",
    "version": "15.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "assets": {
        "web.assets_tests": [
            "/website_sale_invoice_address/static/src/js/website_sale_invoice_address_tour.js"
        ]
    },
}
