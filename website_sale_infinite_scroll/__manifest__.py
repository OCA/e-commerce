# Copyright 2020 Advitus MB
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "eCommerce Infinite Scroll",
    "category": "Website",
    "version": "14.0.1.0.0",
    "author": "Advitus MB, Ooops, Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "LGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/assets.xml",
        "views/templates.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [
        "demo/demo_products.xml",
    ],
    "maintainers": ["dessanhemrayev", "CetmixGitDrone"],
    "application": False,
    "installable": True,
}
