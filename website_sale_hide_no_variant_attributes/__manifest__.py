# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Hide No Variant Attributes",
    "summary": "Exclude non-variant-defining attributes from the variant "
    "selector and its exclusion rules",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/variant_templates.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "website_sale_hide_no_variant_attributes/static/tests/**/*",
        ],
    },
}
