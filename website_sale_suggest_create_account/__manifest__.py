# Copyright (C) 2015 Antiun Ingeniería, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Suggest to create user account when buying",
    "summary": "Suggest users to create an account when buying in the website",
    "version": "13.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce/",
    "author": "Tecnativa, " "LasLabs, " "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/website_sale.xml", "views/assets.xml"],
    "post_init_hook": "post_init_hook",
}
