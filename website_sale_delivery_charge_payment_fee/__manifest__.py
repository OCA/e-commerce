# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "eCommerce: charge payment fee (Delivery)",
    "summary": "Payment fee charged to customer",
    "version": "12.0.1.0.1",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Quartile Limited, "
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale_charge_payment_fee", "website_sale_delivery"],
    "data": ["views/website_sale_templates.xml"],
}
