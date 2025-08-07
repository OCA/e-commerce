# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Account Financial Risk",
    "version": "16.0.1.0.0",
    "category": "E-Commerce",
    "summary": "",
    "license": "AGPL-3",
    "depends": ["account_financial_risk", "website_sale"],
    "data": [
        "templates/payment_custom_templates.xml",
        "templates/website_sale_templates.xml",
        "data/payment_provider_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_financial_risk/static/src/js/post_processing.js",
        ],
    },
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "installable": True,
}
