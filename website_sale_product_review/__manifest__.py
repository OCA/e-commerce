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
    "depends": ["website_sale", "sales_team", "website", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/product_review_rules.xml",
        "views/product_review_views.xml",
        "views/product_template_views.xml",
        "views/reviewers_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_review/static/src/css/reviews.css",
            "website_sale_product_review/static/src/store.esm.js",
            "website_sale_product_review/static/src/components/review_form/review_form.esm.js",
            "website_sale_product_review/static/src/components/reviews/reviews.esm.js",
            "website_sale_product_review/static/src/main.esm.js",
        ],
    },
    "installable": True,
    "application": False,
}
