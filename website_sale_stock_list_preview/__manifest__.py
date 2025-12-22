# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Stock List Preview",
    "summary": "Show the stock of products on the product previews",
    "version": "18.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["website_sale_stock"],
    "data": ["views/templates.xml"],
    "assets": {
        "web.assets_tests": [
            "/website_sale_stock_list_preview/static/src/tests/*.esm.js",
        ],
    },
}
