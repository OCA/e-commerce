# Copyright 2026 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Address Lock",
    "summary": "Keep customers from adding or editing addresses on the website",
    "version": "17.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Binhex, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/res_partner_views.xml",
        "views/website_sale_templates.xml",
        "views/portal_templates.xml",
    ],
    "images": ["static/description/checkout_locked.png"],
    "installable": True,
}
