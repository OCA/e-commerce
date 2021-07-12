# Copyright 2015, 2017, 2021 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Cristina Martin R.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require accepting legal terms to checkout",
    "summary": "Force the user to accept legal tems to buy in the web shop",
    "version": "13.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_legal_page", "website_sale"],
    "data": ["templates/website_sale.xml", "templates/assets.xml"],
}
