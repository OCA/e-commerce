# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Stock Location Filter",
    "summary": "Choose which stock locations count towards the stock "
    "quantity displayed on the website shop.",
    "version": "19.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website/Website",
    "depends": [
        "website_sale_stock",
    ],
    "data": [
        "views/stock_location_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
