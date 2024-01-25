#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Clear e-commerce cart",
    "summary": "Show button to empty the e-commerce cart.",
    "version": "16.0.1.0.0",
    "author": "Aion Tech, Odoo Community Association (OCA)",
    "maintainers": [
        "SirAionTech",
    ],
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_cart_clear/static/src/js/widget.js",
        ],
        "web.assets_tests": [
            "website_sale_cart_clear/static/src/tests/tours/tour.js",
        ],
    },
}
