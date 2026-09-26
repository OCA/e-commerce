# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Webshop VIES Populator",
    "summary": "Autofill name, address from VIES data in webshop",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales/CRM",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA), "
    "The Open Source Company B.V.",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "partner_data_vies_populator",
        "website_sale",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_vies_populator/static/src/website_sale.js",
        ],
    },
}
