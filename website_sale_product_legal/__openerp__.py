# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Legal terms per product",
    "summary": "Make buyers to accept legal terms per product",
    "version": "9.0.1.0.0",
    "category": "e-commerce",
    "website": "http://www.antiun.com",
    "author": "Antiun Ingeniería S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/legal_term_view.xml",
        "views/product_template_view.xml",
        "views/templates.xml",
    ],
}
