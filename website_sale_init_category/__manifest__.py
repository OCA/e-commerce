# Copyright 2021 Manuel Calero <https://xtendoo.es/>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Website Sale Init Category",
    "summary": """It allows to establish an initial category in electronic commerce,
                if the category is established, the menu "All products" is hidden.""",
    "version": "13.0.1.1.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce/",
    "author": "Xtendoo, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["portal", "website", "website_sale"],
    "data": [
        "views/assets.xml",
        "views/website_sale_templates.xml",
        "views/res_config_settings_views.xml",
    ],
}
