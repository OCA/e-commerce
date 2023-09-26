# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Cart Quantity",
    "summary": "Allows to add to cart from product items a custom quantity.",
    "version": "15.0.1.1.0",
    "website": "https://github.com/OCA/e-commerce",
    "maintainers": ["CarlosRoca13"],
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_product_item_cart_custom_qty/static/src/scss/add_to_cart.scss"
        ],
        "web.assets_tests": [
            "/website_sale_product_item_cart_custom_qty/static/src/js/tour.js"
        ],
    },
}
