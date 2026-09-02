# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Document Variant",
    "summary": "Publish and refresh variant-specific documents on the product page",
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
        "views/product_document_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_document_variant/static/src/interactions/**/*",
        ],
    },
}
