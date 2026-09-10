# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale - Product Assurance Icons",
    "summary": "Show configurable assurance/trust icons on the product page",
    "version": "19.0.1.0.0",
    "author": "Domatix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website/Website",
    "depends": ["website_sale"],
    "data": [
        "security/website_sale_product_assurance_icons_security.xml",
        "views/res_config_settings_views.xml",
        "views/website_sale_assurance.xml",
        "wizard/website_sale_assurance_config_views.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_assurance_icons/static/src/scss/website_sale_assurance.scss",
        ],
    },
    "demo": [
        "demo/website_sale_assurance.xml",
    ],
    "installable": True,
}
