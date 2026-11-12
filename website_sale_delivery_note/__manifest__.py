# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Delivery Note",
    "summary": "Let the customer leave a delivery note for the carrier",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website/Website Sale",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Domatix, Odoo Community Association (OCA)",
    "maintainers": ["idris-domatix"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale", "delivery", "stock_delivery"],
    "data": [
        "views/website_checkout_templates.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_delivery_note/static/src/js/website_sale_delivery_note.js",
        ],
    },
}
