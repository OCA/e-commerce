# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Secondary Unit",
    "summary": "Allow manage secondary units in website shop",
    "version": "15.0.1.1.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale", "sale_order_secondary_unit"],
    "data": [
        "security/ir.model.access.csv",
        "security/website_sale_secondary_unit.xml",
        "views/product_secondary_unit_views.xml",
        "views/product_template_views.xml",
        "views/templates.xml",
    ],
    "demo": ["data/demo.xml"],
    "post_init_hook": "post_init_hook",
    "assets": {
        "web.assets_frontend": [
            "/website_sale_secondary_unit/static/src/js/website_sale_secondary_unit.js",
            "/website_sale_secondary_unit/static/src/scss/website_sale_secondary_unit.scss",
        ],
        "web.assets_tests": [
            "/website_sale_secondary_unit/static/src/js/website_sale_secondary_unit_tour.js"
        ],
    },
}
