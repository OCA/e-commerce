# Copyright 2020 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "eCommerce Category Descriptions",
    "summary": "Display a description for each eCommerce category",
    "version": "12.0.1.0.2",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Yajo"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "templates/website_sale.xml",
    ],
}
