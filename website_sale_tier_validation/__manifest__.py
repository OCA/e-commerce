# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "eCommerce tier validation",
    "summary": "Adds tier validation control to ecommerce purchase orders",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["CarlosRoca13"],
    "installable": True,
    "depends": ["sale_tier_validation", "website_sale"],
    "data": ["data/mail_template_validation.xml", "templates/templates.xml"],
}
