# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale UoM Continuous",
    "summary": "Sell decimal quantities of products in continuous UoMs (kg, L, m, ...)",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "depends": ["website_sale"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_uom_continuous/static/src/**/*",
        ],
        "web.assets_tests": [
            "website_sale_uom_continuous/static/tests/tours/**/*",
        ],
    },
}
