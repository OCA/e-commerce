# Copyright 2021 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale Wishlist Keep",
    "category": "Website",
    "summary": 'Allows to add products to my cart but keep it in my wishlist"',
    "development_status": "Production/Stable",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["website_sale_wishlist"],
    "website": "https://github.com/OCA/e-commerce",
    "data": ["views/website_sale_wishlist_template.xml"],
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "installable": True,
    "assets": {
        "web.assets_tests": ["/website_sale_wishlist_keep/static/src/js/tour.esm.js"]
    },
}
