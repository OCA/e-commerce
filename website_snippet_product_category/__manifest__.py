# Copyright 2020 Tecnativa - Alexandre Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Website Snippet Product Category",
    "category": "Website",
    "summary": "Adds a new snippet to show e-commerce categories",
    "version": "13.0.2.1.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "depends": ["website_sale"],
    "data": [
        "templates/assets.xml",
        "templates/snippets.xml",
        "views/product_public_category.xml",
    ],
    "demo": ["demo/demo.xml", "demo/pages.xml"],
    "maintainers": ["Tardo"],
    "installable": True,
}
