# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Tax Toggle",
    "summary": "Allow display price in Shop with or without taxes",
    "version": "16.0.1.0.0",
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
            "/website_sale_tax_toggle/static/src/scss/website_sale_tax_toggle.scss",
        ],
        "web.assets_tests": [
            "/website_sale_tax_toggle/static/src/js/website_sale_tax_toggle_tour.esm.js"
        ],
    },
}
