# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Comparison Hide Price",
    "version": "13.0.2.0.0",
    "category": "Website",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Hide product prices on the shop",
    "depends": ["website_sale_hide_price", "website_sale_comparison"],
    "data": ["views/website_sale_template.xml"],
    "installable": True,
    "auto_install": True,
}
