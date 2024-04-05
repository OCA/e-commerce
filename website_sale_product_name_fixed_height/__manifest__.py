# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Description On N Rows",
    "version": "16.0.1.0.0",
    "category": "Website",
    "author": "Ooops, Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": """This module lets user set for each website how many lines
                of description to display in /shop page""",
    "depends": ["website_sale"],
    "data": ["views/website_sale_template.xml", "views/res_config_settings_view.xml"],
    "installable": True,
}
