# Copyright 2021 Studio73 - Miguel Gandia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale Attribute Filter Range",
    "category": "Website",
    "summary": "Add range display type for product and new range filter for it",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["website_sale"],
    "data": [
        "templates/website_sale.xml",
        "templates/sale.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_attribute_filter_range/static/src/scss/shop.scss",
            "website_sale_attribute_filter_range/static/src/js/shop.js",
            "website_sale_attribute_filter_range/static/src/lib/ionRangeSlider/*.css",
            "website_sale_attribute_filter_range/static/src/lib/ionRangeSlider/*.js",
        ],
    },
    "author": "Studio73, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "installable": True,
    "maintainers": ["Studio73"],
}
