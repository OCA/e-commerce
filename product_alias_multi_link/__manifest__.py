# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Multi Links (Alias)",
    "version": "14.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": [
        "product_template_multi_link",
        "product_variant_multi_link",
        "shopinvader_product_alias",
    ],
    "data": [
        "views/product_template_link_view.xml",
    ],
    "installable": True,
}
