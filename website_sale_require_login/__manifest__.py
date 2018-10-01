# Copyright 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require login to checkout",
    "summary": "Force users to login for buying",
    "version": "12.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "website_sale_suggest_create_account",
        "web_tour",
    ],
    "data": [
        "views/website_sale.xml",
    ],
    'demo': [
        "demo/demo_assets.xml",
    ],
}
