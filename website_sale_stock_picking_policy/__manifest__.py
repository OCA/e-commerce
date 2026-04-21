# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale - Stock Picking Policy",
    "summary": "Let customers choose consolidated delivery at checkout",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website/Website",
    "depends": [
        "website_sale",
        "sale_stock",
    ],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_stock_picking_policy/static/src/js/picking_policy.esm.js",
        ],
    },
}
