# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Stock Provisioning Date",
    "summary": "Display provisioning date for a product in shop online",
    "version": "17.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale_stock"],
    "data": ["views/product_template_views.xml"],
    "assets": {
        "web.assets_frontend": [
            "website_sale_stock_provisioning_date/static/src/xml/"
            "website_sale_stock_product_availability.xml",
        ],
        "web.assets_tests": [
            "/website_sale_stock_provisioning_date/static/src/js/"
            "website_sale_stock_provisioning_date_tour.esm.js",
        ],
    },
}
