# Copyright 2020 Commown SCIC SAS (https://commown.coop)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Slimpay online payment and mandate signing for e-commerce",
    "summary": "Provide your website customers seamless online SEPA mandate signing with Slimpay",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "e-commerce",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Commown SCIC SAS, Odoo Community Association (OCA)",
    "maintainers": ["fcayre"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale", "account_payment_slimpay"],
    "data": [
        "views/address_template.xml",
    ],
}
