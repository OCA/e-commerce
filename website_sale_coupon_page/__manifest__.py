# Copyright 2021 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Coupon Page",
    "version": "13.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale_coupon"],
    "data": [
        "security/ir.model.access.csv",
        "templates/assets.xml",
        "views/sale_coupon_program_views.xml",
        "templates/promotion_templates.xml",
    ],
}
