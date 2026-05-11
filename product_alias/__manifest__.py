# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Alias",
    "summary": "Alias for each product attribute values's configuration",
    "version": "18.0.1.0.0",
    "category": "E-Commerce",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product",
    ],
    "data": [
        "views/product_template.xml",
        "security/ir.model.access.csv",
    ],
}
