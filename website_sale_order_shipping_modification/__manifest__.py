# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Order Shipping Modification",
    "summary": "Change the delivery address in quotes from the portal",
    "version": "16.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "views/sale_portal_templates.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_sale_order_shipping_modification/static/src/js/hide_header_footer.js",
        ],
    },
}
