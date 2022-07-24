# Copyright 2019 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Detail Attribute Value Image",
    "summary": "Display attributes values images in shop product detail",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "views/product_attribute_value_views.xml",
        "templates/shop_product.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_product_detail_attribute_value_image/static/src/scss/style.scss"
        ],
        "web.assets_tests": [
            "/website_sale_product_detail_attribute_value_image/static/src/js/"
            "website_sale_product_detail_attribute_value_image_tour.js",
        ],
    },
}
