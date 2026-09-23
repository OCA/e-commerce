{
    "name": "Website Sale Dynamic Review Snippet",
    "version": "18.0.1.0.0",
    "category": "Website",
    "depends": ["website_sale"],
    "summary": (
        "Aggregate website users’ reviews from product templates into a single "
        "website snippet (configurable, up to 100 records) "
        "accessible in the Odoo Website Builder."
    ),
    "author": "XXP, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "data": [
        "views/snippets/options.xml",
        "views/snippets/s_dynamic_review.xml",
    ],
    "assets": {
        "portal.assets_chatter": [
            "website_sale_dynamic_review_snippet/static/src/core/*",
            "website_sale_dynamic_review_snippet/static/src/components/*",
            "website_sale_dynamic_review_snippet/static/src/services/*",
        ],
        "web.assets_frontend": [
            "website_sale_dynamic_review_snippet/static/src/boot/boot_service.esm.js",
        ],
        "web.assets_tests": [
            "website_sale_dynamic_review_snippet/static/src/tests/*.esm.js"
        ],
    },
}
