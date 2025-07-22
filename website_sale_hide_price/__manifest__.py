# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Hide Price",
    "version": "17.0.1.2.0",
    "category": "Website",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Hide product prices on the shop",
    "depends": ["website_sale"],
    "data": [
        "data/product_snippet_template_data.xml",
        "views/partner_view.xml",
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/website_sale_template.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_frontend": [
            "/website_sale_hide_price/static/src/xml/website_sale_templates.xml"
        ]
    },
}
