# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product Alias",
    "summary": "Alias for each product attribute values's configuration",
    "version": "14.0.1.0.0",
    "category": "Shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "shopinvader",
    ],
    "data": [
        "views/product_template.xml",
        "security/ir.model.access.csv",
    ],
}
