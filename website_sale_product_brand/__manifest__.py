# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Brand Filtering in Website",
    "category": "e-commerce",
    "author": "Serpent Consulting Services Pvt. Ltd., "
    "Tecnativa, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "version": "19.0.2.0.0",
    "license": "AGPL-3",
    "depends": ["product_brand", "website", "website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/website_menu.xml",
        "views/product_brand.xml",
        "views/product_brand_views.xml",
        "views/res_config_settings_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_product_brand/static/src/scss/website_sale_product_brand.scss",
            (
                "after",
                "website_sale/static/src/interactions/website_sale.js",
                "/website_sale_product_brand/static/src/interactions/website_sale_brand_filter.esm.js",
            ),
        ],
        "web.assets_tests": [
            "/website_sale_product_brand/static/src/js/tour.esm.js",
            "/website_sale_product_brand/static/src/js/test_website_sale_filter_brand.esm.js",
        ],
    },
    "installable": True,
}
