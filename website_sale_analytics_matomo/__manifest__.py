# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Matomo Ecommerce tracker",
    "version": "16.0.1.0.0",
    "author": "Onestein,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Tracking Ecommerce Actions in Matomo",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_analytics_matomo",
        "website_sale",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_analytics_matomo/static/src/js/website_sale_tracking.js",
        ],
    },
    "installable": True,
    "auto_install": True,
}
