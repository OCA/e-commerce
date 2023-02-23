# Copyright 2015, 2017, 2021 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Cristina Martin R.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require accepting legal terms to checkout",
    "summary": "Force the user to accept legal tems to buy in the web shop",
    "version": "15.0.2.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["templates/website_sale.xml"],
    "assets": {
        "web.assets_frontend": [
            "//website_sale_require_legal/static/src/scss/website_sale_require_legal.scss",
        ],
        "web.assets_tests": [
            "/website_sale_require_legal/static/tests/tours/tour.js",
        ],
    },
}
