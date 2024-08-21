# Ooops
# Cetmix
# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Website Sale Cart Quantity Shop",
    "summary": "Choose cart quantity from shop page",
    "category": "Website",
    "version": "14.0.1.1.0",
    "author": "AvanzOSC, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "website_sale",
    ],
    "data": [
        "views/assets.xml",
        "views/website_sale.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
