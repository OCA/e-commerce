# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Order Cancel",
    "version": "15.0.1.0.1",
    "summary": "Allow customers to cancel their website sale orders",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale", "sale_management"],
    "data": ["views/templates.xml", "views/res_config_settings_views.xml"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_order_cancel/static/src/js/website_sale_order_cancel.js"
        ],
        "web.assets_tests": [
            "website_sale_order_cancel/static/tests/tours/cancel_order_tour.js",
        ],
    },
}
