# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Document Type",
    "summary": "Group published product documents by type on the product page",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website",
    "depends": [
        "product_document_type",
        "website_sale",
    ],
    "data": [
        "views/templates.xml",
    ],
    "auto_install": True,
    "installable": True,
}
