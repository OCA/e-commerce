# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product matrix with secondary units in eCommerce",
    "version": "17.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website",
    "maintainers": ["pilarvargas-tecnativa"],
    "depends": [
        "website_sale_product_matrix",
        "sale_product_matrix_secondary_unit",
    ],
    "data": [
        "templates/product_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_secondary_unit_product_matrix/static/src/js/**/*.js",
        ],
    },
}
