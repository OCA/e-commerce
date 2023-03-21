# Copyright 2021 Studio73 - Ioan Galan
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Attribute Filter Multiselect",
    "category": "E-Commerce",
    "summary": "Add multiselect display type for product and new filter for it",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "templates/sale.xml",
        "templates/website_sale.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_attribute_filter_multiselect/static/src/lib/multiple-select/multiple-select.js",  # noqa: B950
            "website_sale_attribute_filter_multiselect/static/src/lib/multiple-select/multiple-select-locale-all.js",  # noqa: B950
            "website_sale_attribute_filter_multiselect/static/src/js/website_sale.js",
            "website_sale_attribute_filter_multiselect/static/src/lib/multiple-select/multiple-select.css",  # noqa: B950
            "website_sale_attribute_filter_multiselect/static/src/scss/website_sale.scss",
        ]
    },
    "author": "Studio73, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "installable": True,
}
