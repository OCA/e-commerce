{
    "name": "Website Sale Float Cart Quantity",
    "summary": "Allow float quantities in cart for website sale module",
    "version": "16.0.1.0.0",
    "category": "Website",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "author": "AvanzOSC, Odoo Community Association (OCA)",
    "depends": [
        "website_sale",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_float_cart_qty/static/src/js/float_qty.js",
        ],
    },
    "installable": True,
}
