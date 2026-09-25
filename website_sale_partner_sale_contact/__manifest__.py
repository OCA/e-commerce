# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Partner Sale Contact",
    "summary": "Set the parent company as customer and the contact as sale "
    "contact on website orders",
    "version": "19.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "website_sale",
        "sale_partner_sale_contact",
    ],
}
