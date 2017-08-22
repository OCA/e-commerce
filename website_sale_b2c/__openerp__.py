# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "e-Commerce B2C mode",
    "summary": "Display prices with taxes included in your online shop",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://www.tecnativa.com/",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "wizards/sale_config_settings.xml",
        "templates/website_sale.xml",
    ],
}
