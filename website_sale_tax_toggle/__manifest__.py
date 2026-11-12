# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Tax Toggle",
    "summary": "Allow display price in Shop with or without taxes",
    "version": "20.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_tax_toggle/static/src/js/website_sale_tax_toggle.esm.js",
        ],
        "web.assets_tests": [
            "/website_sale_tax_toggle/static/src/tests/website_sale_tax_toggle_tour.esm.js"
        ],
        "website.website_builder_assets": [
            "website_sale_tax_toggle/static/src/website_builder/tax_toggle_option.xml",
        ],
    },
}
