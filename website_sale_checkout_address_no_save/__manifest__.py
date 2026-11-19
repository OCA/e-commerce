# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Website Sale Not Save Address",
    "summary": "Avoid having to many address as dropshipping customer",
    "version": "18.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/website_sale_templates.xml"],
    "assets": {
        "web.assets_tests": [
            "website_sale_checkout_address_no_save/static/tests/tours/*.js",
        ],
    },
}
