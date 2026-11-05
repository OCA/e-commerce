# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Product Accessory Hide Price",
    "summary": "Hide prices of the suggested accessories on the product page",
    "version": "19.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "depends": ["website_sale_hide_price", "website_sale_product_accessory"],
    "data": [
        "views/website_sale_templates.xml",
    ],
    "installable": True,
    "auto_install": True,
}
