# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Attribute Filter Category",
    "summary": "Allow group attributes in shop by categories",
    "version": "15.0.2.1.0",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale_comparison"],
    "data": [
        "views/templates.xml",
        "views/website_sale_product_attribute_filter_category_view.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_product_attribute_filter_category/static/src/scss/*.scss",
        ],
        "web.assets_tests": [
            "/website_sale_product_attribute_filter_category/static/src/js/*.js"
        ],
    },
}
