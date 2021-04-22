# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Survey for products in eCommerce",
    "summary": "Ask buyers to answer a survey in checkout wizard",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Yajo"],
    "license": "AGPL-3",
    "depends": ["website_sale", "website_survey"],
    "data": [
        "templates/survey.xml",
        "templates/website_sale.xml",
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
    ],
    "demo": [
        "demo/assets.xml",
    ],
}
