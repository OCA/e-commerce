# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Style Custom Badge",
    "version": "13.0.1.0.0",
    "category": "Website",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Define custom badges for your e-commerce products",
    "depends": ["website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/menus.xml",
        "templates/assets.xml",
        "templates/website_sale.xml",
        "views/product_style_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "maintainers": ["Tardo"],
}
