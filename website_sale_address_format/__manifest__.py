# Copyright 2020-2022 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Address Format",
    "summary": "Customize eCommerce address field layout by country",
    "version": "17.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website/Website",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": ["views/res_country_views.xml"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_address_format/static/src/js/website_sale_address_format.esm.js",
        ],
    },
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
