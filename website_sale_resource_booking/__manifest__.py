# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sell resource booking products in your eCommerce",
    "summary": "Let customers book resources temporarily before buying",
    "version": "12.0.1.0.1",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Yajo"],
    "license": "AGPL-3",
    "depends": ["sale_resource_booking", "website_sale"],
    "data": [
        "data/ir_cron_data.xml",
        "templates/assets.xml",
        "templates/website_sale.xml",
        "views/product_template_view.xml",
    ],
    "demo": [
        "demo/assets.xml",
    ],
}
