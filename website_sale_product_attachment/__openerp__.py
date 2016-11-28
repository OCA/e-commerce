# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Offer Product Attachments",
    "version": "9.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "add attachments to products and show them in shop",
    "depends": [
        'website_sale'
    ],
    "data": [
        'views/attachements_view.xml',
        'views/product_attachment.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
