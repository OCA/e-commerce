# Copyright 2021 Valentín Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Account Fiscal Position Partner Type",
    "version": "13.0.0.0.1",
    "category": "Website",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Sygel Technology," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "development_status": "Beta",
    "depends": ["account_fiscal_position_partner_type", "website_sale"],
    "data": ["views/website_sale.xml"],
}
