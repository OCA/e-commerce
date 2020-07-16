# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "eCommerce: charge payment fee",
    "summary": "Payment fee charged to customer",
    "version": "11.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Agile Business Group, AITIC S.A.S, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/payment_view.xml",
        "templates/website_sale.xml"
    ],
}
