# Copyright 2020 Tecnativa - Jairo Llopis
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "eCommerce product attachments",
    "summary": "Let visitors download attachments from a product page",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Yajo"],
    "license": "LGPL-3",
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "templates/product_template.xml",
        "views/ir_attachment.xml",
        "views/product_template.xml",
    ],
    "demo": ["demo/assets.xml"],
}
