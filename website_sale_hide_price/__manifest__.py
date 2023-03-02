# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Hide Price",
    "version": "13.0.2.1.0",
    "category": "Website",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Hide product prices on the shop",
    "depends": ["website_sale"],
    "data": [
        "views/assets.xml",
        "views/partner_view.xml",
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/website_sale_template.xml",
    ],
    "qweb": ["static/src/xml/website_sale_templates.xml"],
    "installable": True,
}
