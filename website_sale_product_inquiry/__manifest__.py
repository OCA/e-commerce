# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Sale Product Inquiry",
    "summary": "Add a product inquiry button and popup form on eCommerce product pages",
    "version": "19.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
        "crm",
    ],
    "data": [
        "views/crm_lead_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_inquiry/static/src/js/product_inquiry.esm.js",
        ],
    },
}
