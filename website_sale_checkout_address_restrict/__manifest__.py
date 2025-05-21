# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Checkout Address Restrict",
    "version": "15.0.1.0.0",
    "summary": "Restrict checkout address workflow",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/website_sale_templates.xml", "views/res_config_settings_views.xml"],
}
