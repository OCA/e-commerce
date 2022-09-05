# Copyright 2020-2022 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Address Format",
    "version": "15.0.1.0.0",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website/Website",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": ["views/res_country_views.xml"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_address_format/static/src/js/website_sale_address_format.js",
        ],
    },
    "installable": True,
}
