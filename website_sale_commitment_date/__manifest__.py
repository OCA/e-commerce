# Copyright 2025 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Commitment Date",
    "version": "16.0.1.0.0",
    "category": "Website",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Allow to set a commitment date on the sale order from to the e-commerce",
    "depends": ["website_sale_delivery"],
    "data": [
        "security/ir.model.access.csv",
        "views/delivery_carrier_views.xml",
        "views/delivery_carrier_templates.xml",
        "data/delivery_carrier_weekday_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_commitment_date/static/src/**/*",
        ],
    },
}
