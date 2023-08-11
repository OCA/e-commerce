# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Attribute Filter Collapse",
    "summary": "Allows the attributes of the categories to be folded",
    "version": "16.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/templates.xml",
        "views/snippets/snippets.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_attribute_filter_collapse/static/src/scss/*",
        ],
        "web.assets_tests": [
            "website_sale_product_attribute_filter_collapse/static/src/js/*",
        ],
    },
}
