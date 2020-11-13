# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Sale Stock Picking Note",
    "summary": "Allows to set comments on website orders",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    "version": "12.0.1.0.0",
    'maintainers': ['CarlosRoca13'],
    "category": "Website",
    "depends": ["website_sale", "sale_stock_picking_note"],
    "data": [
        "views/assets.xml",
        "data/data.xml",
        "views/customer_comment_config_view.xml",
        "views/template.xml",
    ],
    "installable": True,
}
