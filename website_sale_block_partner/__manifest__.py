# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Block Partner",
    "summary": "This module help to blacklist partners description",
    "version": "15.0.1.0.0",
    "category": "Contact",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "contacts",
        "website_sale_wishlist",
        "website_sale_comparison",
        "sale_management",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "views/templates.xml",
    ],
    "installable": True,
    "application": False,
}
