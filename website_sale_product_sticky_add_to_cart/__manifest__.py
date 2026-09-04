# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Product Sticky Add to Cart",
    "summary": "Show a sticky add-to-cart bar on the product page while scrolling",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website/Website Sale",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Domatix, Odoo Community Association (OCA)",
    "maintainers": ["idris-domatix"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/product_templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_product_sticky_add_to_cart/static/src/interactions/*.esm.js",
            "/website_sale_product_sticky_add_to_cart/static/src/scss/website_sale_product_sticky_add_to_cart.scss",
        ],
        "web.assets_tests": [
            "/website_sale_product_sticky_add_to_cart/static/src/js/tour.esm.js",
        ],
    },
}
