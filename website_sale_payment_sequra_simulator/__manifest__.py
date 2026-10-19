# Copyright 2025 Juan Carlos Oñate - Tecnativa <juancarlos.onate@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Payment Sale SeQura Simulator",
    "summary": "Adds SeQura payment simulator.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Payment Providers",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["juancarlosonate-tecnativa"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "depends": ["website_sale", "payment_sequra"],
    "data": [
        "views/payment_provider_views.xml",
        "views/templates.xml",
    ],
    "installable": True,
}
