# Copyright 2021 Valentín Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Account Fiscal Position Partner Type",
    "version": "15.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Sygel Technology," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "development_status": "Beta",
    "depends": ["account_fiscal_position_partner_type", "website_sale"],
    "data": [
        "views/website_sale.xml",
        "views/portal_templates.xml",
        "views/auth_signup_login_templates.xml",
    ],
}
