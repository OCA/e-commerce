# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Website Sale Checkout Country VAT",
    "summary": "Autocomplete VAT in checkout process",
    "version": "14.0.1.0.1",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base_vat", "website_sale", "website_snippet_country_dropdown"],
    "data": ["views/assets.xml", "views/templates.xml"],
}
