# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Empty Cart",
    "summary": "Adds a button in the website cart to empty all",
    "version": "17.0.1.0.0",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/cart_templates.xml",
        "views/res_config_settings.xml",
    ],
}
