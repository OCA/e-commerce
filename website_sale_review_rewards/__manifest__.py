# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Review Rewards",
    "summary": "Award gift points and rewards to customers who review products",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "Odoo Community Association (OCA), Kencove",
    "maintainers": ["Kencove"],
    "license": "LGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_sale",
        "gamification",
    ],
    "data": [
        "data/gamification_goal_definition.xml",
    ],
    "assets": {},
    "demo": [],
    "installable": True,
    "application": False,
}
