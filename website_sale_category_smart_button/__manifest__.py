# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Category Smart Button",
    "summary": "Adds a 'Go to Website' smart button on the eCommerce category"
    " form view",
    "version": "19.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JasminSForgeFlow"],
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "category": "Website",
    "depends": ["website_sale"],
    "data": [
        "views/product_public_category_views.xml",
    ],
    "installable": True,
}
