{
    "name": "Ecommerce First last name",
    "category": "other",
    "version": "15.0.1.0.0",
    "author": "Nitrokey GmbH," "Odoo Community Association (OCA)",
    "summary": """Ecommerce First last name""",
    "sequence": "1",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ecommerce_first_last_name/static/src/js/**/*",
        ],
    },
}
