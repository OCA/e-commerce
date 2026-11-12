# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Product Compare Price",
    "summary": "Show the variant compare price, discount badge and saved amount",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website/Website Sale",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Domatix, Odoo Community Association (OCA)",
    "maintainers": ["idris-domatix"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/product_templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_product_compare_price/static/src/js/website_sale_product_compare_price.esm.js",
        ],
        "web.assets_tests": [
            "/website_sale_product_compare_price/static/src/js/tour.esm.js",
        ],
    },
}
