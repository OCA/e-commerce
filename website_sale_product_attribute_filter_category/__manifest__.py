# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Attribute Filter Category",
    "summary": "Allow group attributes in shop by categories",
    "version": "14.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale_comparison"],
    "data": [
        "views/assets.xml",
        "views/templates.xml",
        "views/product_attribute_category.xml",
    ],
}
