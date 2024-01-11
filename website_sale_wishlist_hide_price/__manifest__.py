# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Wishlist Hide Price",
    "version": "16.0.1.0.0",
    "category": "Website",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Hide product prices on the shop",
    "depends": ["website_sale_hide_price", "website_sale_wishlist"],
    "data": ["views/website_sale_template.xml"],
    "installable": True,
    "auto_install": True,
    "assets": {
        "web.assets_tests": [
            "/website_sale_wishlist_hide_price/static/tests/tours/*.js",
        ]
    },
}
