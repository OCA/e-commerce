# Author: Maciej Wichowski. Copyright: Versada UAB.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Website Sale Stock Hide Price on Wishlist",
    "version": "17.0.1.0.0",
    "summary": "Hide product prices on the wishlist",
    "license": "AGPL-3",
    "author": "Versada, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website",
    "depends": [
        # odoo
        "website_sale_stock_wishlist",
        # OCA:e-commerce
        "website_sale_hide_price_wishlist",
    ],
    "data": ["views/website_sale_templates.xml"],
    "installable": True,
    "auto_install": True,
}
