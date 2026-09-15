# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale Attribute Filter Order",
    "version": "19.0.1.0.0",
    "category": "Website",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "LGPL-3",
    "summary": "Move active checkbox options to the first place of the list",
    "depends": ["website_sale"],
    "data": ["templates/website_sale.xml"],
    "assets": {
        "website.website_builder_assets": [
            "website_sale_product_attribute_filter_order/static/src/website_builder/**/*",
        ],
    },
    "installable": True,
    "maintainers": ["Tardo"],
}
