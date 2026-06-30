# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Tax Selection",
    "summary": "Select e-commerce tax display by website partner",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["yankinmax"],
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
