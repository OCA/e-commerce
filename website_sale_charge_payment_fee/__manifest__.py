# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "eCommerce: charge payment fee",
    "summary": "Payment fee charged to customer",
    "version": "12.0.1.1.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Agile Business Group, "
    "AITIC S.A.S, "
    "Quartile Limited, "
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/payment_acquirer_views.xml", "views/website_sale_templates.xml"],
}
