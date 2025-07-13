# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Customer Reviews",
    "summary": "Allow customers to leave reviews on products",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "Odoo Community Association (OCA), Kencove",
    "maintainers": ["Kencove"],
    "license": "LGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_sale",
        "sales_team",
        "website",
        "mail",
        "portal",
        "portal_rating",
    ],
    "data": [
        "views/reviewers_template.xml",
    ],
    "assets": {
        "portal.assets_chatter": [
            "website_sale_customer_reviews/static/src/bar_chart.xml",
            "website_sale_customer_reviews/static/src/bar_chart.esm.js",
            "website_sale_customer_reviews/static/src/thread.xml",
            "website_sale_customer_reviews/static/src/thread.esm.js",
        ],
        "web.assets_tests": [
            "website_sale_customer_reviews/static/src/test/test.esm.js",
        ],
    },
    "demo": [
        "demo/product_demo.xml",
    ],
    "installable": True,
    "application": False,
}
