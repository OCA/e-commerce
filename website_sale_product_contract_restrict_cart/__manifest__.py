# Copyright 2023 Onestein- Anjeel Haria
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Website Sale Product Contract Cart",
    "summary": "Restricts contracted products from being added with other products in the cart",
    "version": "16.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Onestein, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["website_sale", "product_contract"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_contract_restrict_cart/static/src/js/website_sale_utils.js",
        ],
    },
}
