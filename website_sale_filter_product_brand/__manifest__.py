{
    "name": "Website Sale Filter Product Brand",
    "author": "Advitus MB, Ooops, Cetmix, Odoo Community Association (OCA)",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website/Website",
    "depends": ["product_brand", "website_sale"],
    "demo": [
        "demo/product_brand_demo.xml",
        "demo/product_product_demo.xml",
    ],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "website_sale_filter_product_brand/static/src/tests/tours/test_website_sale_filter_brand.esm.js",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
