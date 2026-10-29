# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Payment Provider: Payplug",
    "version": "19.0.1.1.0",
    "category": "Accounting/Payment Providers",
    "summary": "Payplug payment provider: hosted payment page, refunds",
    "author": "Sébastien Berger (sbinfo67), Odoo Community Association (OCA)",
    "maintainers": ["sbinfo67"],
    "website": "https://github.com/OCA/e-commerce",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": ["payment", "account_payment"],
    "data": [
        "views/payment_payplug_templates.xml",
        "views/payment_provider_views.xml",
        "views/payment_transaction_views.xml",
        "data/payment_provider_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
}
