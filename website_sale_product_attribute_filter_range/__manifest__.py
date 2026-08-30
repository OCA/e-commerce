# Copyright 2025 EthicHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Attribute Range Filter",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Filter products by numeric attribute ranges with a slider",
    "author": "EthicHub, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/product_attribute_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_attribute_filter_range"
            "/static/src/interactions/attribute_range.esm.js",
        ],
    },
    "installable": True,
    "application": False,
}
