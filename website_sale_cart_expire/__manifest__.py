# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Cart Expire",
    "summary": "Cancel carts without activity after a configurable time",
    "version": "15.0.1.1.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "depends": ["website_sale"],
    "data": [
        "data/ir_cron.xml",
        "views/res_config_settings.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_cart_expire/static/src/js/website_sale_cart_expire.js",
        ],
    },
}
