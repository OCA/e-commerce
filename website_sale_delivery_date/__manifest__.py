# Copyright Cetmix OU 2024
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Delivery Date",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Add delivery date selection to e-commerce checkout",
    "author": "Cetmix OU, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "LGPL-3",
    "depends": [
        "website_sale",
        "delivery",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/delivery_carrier_views.xml",
        "views/delivery_form_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_delivery_date/static/src/js/*.js",
        ],
    },
    "installable": True,
    "application": False,
}
