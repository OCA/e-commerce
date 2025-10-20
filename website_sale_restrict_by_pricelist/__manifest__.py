# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Restrict By Pricelist",
    "summary": "Restricts visible products in the website "
    "shop based on the portal user's assigned pricelist.",
    "version": "15.0.1.0.0",
    "category": "eCommerce",
    "website": "https://github.com/OCA/e-commerce",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
