# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "eCommerce product assortment",
    "summary": "Use product assortments to display products available on e-commerce.",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["CarlosRoca13"],
    "installable": True,
    "depends": ["product_assortment", "website_sale"],
    "data": ["templates/assets.xml", "views/ir_filters_views.xml"],
}
