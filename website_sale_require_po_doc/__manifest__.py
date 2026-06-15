# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Require PO Doc",
    "summary": "Request PO number at checkout for customers that require it",
    "version": "19.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale", "sale_require_po_doc"],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_require_po_doc/static/src/js/website_sale_require_po_doc.esm.js",
        ],
        "web.assets_tests": [
            "website_sale_require_po_doc/static/tests/**/*",
        ],
    },
}
