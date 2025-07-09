# Copyright 2020 Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website sale affiliate portal",
    "category": "Website",
    "version": "16.0.1.0.0",
    "author": "Commown SCIC, Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_sale_affiliate_product_restriction",
        "portal",
    ],
    "data": [
        "views/website_portal_sale_templates.xml",
        "views/sale_affiliate.xml",
    ],
    "installable": True,
}
