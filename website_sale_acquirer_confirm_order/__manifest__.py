# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "eCommerce Confirm Order By Payment Provider",
    "summary": "eCommerce Confirm Order By Payment Provider",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "version": "18.0.1.0.0",
    "category": "Website/Website",
    "website": "https://github.com/OCA/e-commerce",
    "maintainers": ["pilarvargas-tecnativa"],
    "license": "AGPL-3",
    "depends": ["payment", "website_sale"],
    "data": [
        "views/payment_provider_views.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "website_sale_acquirer_confirm_order/static/src/js/*",
        ],
    },
    "installable": True,
}
