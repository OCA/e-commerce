# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale Variant Extra Field",
    "summary": "Show variant fields and more field types in the product page "
    "extra fields",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_variant_extra_fields/static/src/js/*.esm.js",
        ],
    },
}
