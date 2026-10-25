# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Product Default Packaging Level",
    "summary": """This module allows to show product default packaging level on product
    details""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_sale",
        "product_packaging_level",
        "sale_product_default_packaging_level",
        "website_sale_product_packaging_level_access",
    ],
    "data": ["views/product_details.xml"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_default_packaging_level/static/src/**/*",
        ],
    },
}
