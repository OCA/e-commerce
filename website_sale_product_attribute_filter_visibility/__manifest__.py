# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Attribute Filter Visibility",
    "summary": "Allow hide any attributes in shop attributes filter",
    "version": "16.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/product_attribute_views.xml"],
    "assets": {
        "web.assets_frontend": [
            (
                "website_sale_product_attribute_filter_visibility/"
                "static/src/js/"
                "website_sale_product_attribute_filter_visibility_tour.js"
            ),
        ],
    },
}
