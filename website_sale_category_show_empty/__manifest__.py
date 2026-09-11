# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Category Show Empty",
    "summary": "Let public and portal visitors open eCommerce category pages"
    " that have no published products",
    "version": "19.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "depends": ["website_sale"],
    "data": [
        "security/product_public_category_security.xml",
        "views/product_public_category_views.xml",
    ],
    "installable": True,
}
