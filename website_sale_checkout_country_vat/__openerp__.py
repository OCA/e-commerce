# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Checkout Country VAT",
    "summary": "Autocomplete VAT in checkout process",
    "version": "8.0.1.0.0",
    "category": "e-commerce",
    'website': 'http://www.tecnativa.com',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
        "website_snippet_country_dropdown",
    ],
    "data": [
        "views/assets.xml",
        "views/res_config.xml",
        "views/templates.xml",
    ],
}
