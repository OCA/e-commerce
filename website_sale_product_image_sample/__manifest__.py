# Copyright 2023 Xtendoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Website sale product image sample",
    "summary": """Display product image sample to select product variant on website""",
    "version": "16.0.1.0.0",
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Xtendoo, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "category": "eCommerce",
    "installable": True,
    "auto_install": False,
    "application": False,
    "depends": [
        "sale",
        "website_sale",
    ],
    "data": [
        "views/variants.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_image_sample/static/src/css/product_configurator.scss",
        ],
    },
}
