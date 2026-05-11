# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Multi Links (Alias)",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": [
        # OCA/e-commerce
        "product_alias",
        "product_variant_multi_link",
    ],
    "data": [
        "views/product_template_link_view.xml",
    ],
    "installable": True,
}
