# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale One Time Delivery Address",
    "summary": "Create one-time delivery contacts from checkout delivery addresses",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "depends": ["sale_stock", "website_sale"],
    "data": [
        "views/res_partner_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_one_time_delivery_address/static/src/interactions/*.js",
        ],
    },
    "installable": True,
}
