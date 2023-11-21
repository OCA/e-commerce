# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "eCommerce product assortment",
    "summary": "Use product assortments to display products available on e-commerce.",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["CarlosRoca13"],
    "installable": True,
    "depends": ["product_assortment", "website_sale"],
    "data": ["views/ir_filters_views.xml"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_assortment/static/src/xml/*.xml",
            "website_sale_product_assortment/static/src/js/variant_mixin.js",
            "website_sale_product_assortment/static/src/js/assortment_list_preview.js",
        ],
        "web.assets_tests": [
            "website_sale_product_assortment/static/src/js/no_purchase_tour.js",
            "website_sale_product_assortment/static/src/js/no_restriction_tour.js",
            "website_sale_product_assortment/static/src/js/no_show_tour.js",
        ],
    },
}
