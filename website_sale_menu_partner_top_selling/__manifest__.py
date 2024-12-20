# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Menu Partner Top Selling",
    "summary": "Displays the user's regular products in the e-commerce.",
    "version": "15.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/res_config_settings_views.xml", "views/templates.xml"],
    "assets": {
        "web.assets_tests": [
            "website_sale_menu_partner_top_selling/static/src/js/tours/*.js"
        ],
    },
}
