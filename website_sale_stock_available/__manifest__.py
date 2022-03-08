# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Stock Available",
    "summary": "Display 'Available to promise' in shop online "
    "instead 'Quantity On Hand'",
    "version": "14.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_available",
        "website_sale_stock",
    ],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
}
