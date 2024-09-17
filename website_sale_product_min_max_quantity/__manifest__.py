# Copyright 2023 Binhex - Nicolás Ramos <n.ramos@binhex.cloud>
# Copyright 2023 Binhex - Adasat Torres <a.torres@binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "website_sale_product_min_max_quantity",
    "summary": """
        This addon allows add the minimum and maximum quantity
        for a product when purchasing on the sales website.
    """,
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "website",
    "version": "16.0.1.0.0",
    "depends": ["website_sale", "website"],
    "data": [
        "views/website_sale_views.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_min_max_quantity/static/src/js/website_sale_utils.js",
        ],
    },
    "maintainer": "nicolasramos-com",
    "installable": True,
}
