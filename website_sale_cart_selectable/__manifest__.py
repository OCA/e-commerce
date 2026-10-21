# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 Tecnativa
# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Sale Cart Selectable",
    "summary": 'Add a toggle to products for enabling "Add to Cart"'
    " functionality in the e-commerce.",
    "version": "16.0.1.0.1",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "OpenSynergy Indonesia, Tecnativa,"
    " Akretion, Coop IT Easy SC, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/product_view.xml",
        "views/website_sale_template.xml",
    ],
    "installable": True,
}
