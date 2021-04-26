# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Force Quantity",
    "summary": "Limit website product purchases to set quantity.",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "maintainers": ["joao-p-marques"],
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/assets.xml",
        "views/website_sale_template.xml",
        "views/product_template.xml",
    ],
}
