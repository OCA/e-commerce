# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Sendcloud eCommerce",
    "summary": "Integrate your web shop with Sendcloud",
    "images": ["static/description/sendcloud_cover.jpeg"],
    "category": "Website/Website",
    "version": "17.0.1.0.0",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "LGPL-3",
    "depends": ["website_sale", "delivery_sendcloud_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/onboarding_data.xml",
        "templates/website_sale_delivery.xml",
        "views/res_config_settings_view.xml",
        "wizards/sendcloud_sync_wizard_view.xml",
        "wizards/sendcloud_website_brand_wizard_view.xml",
        "views/sendcloud_onboarding_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sendcloud_oca/static/src/js/*",
            "website_sendcloud_oca/static/src/xml/*",
        ],
        "web.assets_tests": [
            "website_sendcloud_oca/static/src/tests/**/*",
        ],
    },
    "application": True,
}
