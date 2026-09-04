# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Checkout Skip Payment - Keep as Quotation",
    "summary": "Skip payment in checkout and keep the order as a quotation, "
    "notifying the customer with a dedicated email template.",
    "version": "19.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale_checkout_skip_payment"],
    "data": [
        "data/mail_template_data.xml",
        "views/website_sale_template.xml",
    ],
}
