# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Review",
    "summary": "Allow customers to leave reviews on products",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "Odoo Community Association (OCA), Kencove",
    "maintainers": ["Kencove"],
    "license": "LGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "depends": ["website_sale", "website", "mail"],
    "data": [
        # "security/security.xml",
        # "security/ir.model.access.csv",
        # "views/product_review_views.xml",
        # "views/website_templates.xml",
        # "data/review_data.xml",
        "views/reviewers_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_review/static/src/components/star_rating.esm.js",
            "website_sale_product_review/static/src/main.esm.js",
        ],
    },
    "installable": True,
    "application": False,
}
