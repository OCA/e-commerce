# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Pricelist Item UoM",
    "summary": "Show the price of each packaging on the eCommerce product page",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Website/Website",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
        "product_pricelist_item_uom",
    ],
    "data": [
        "views/variant_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_pricelist_item_uom/static/src/js/interactions/**/*",
        ],
    },
    "installable": True,
    "auto_install": True,
}
