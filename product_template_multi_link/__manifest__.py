# -*- coding: utf-8 -*-
# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Multi Links (Template)',
    'version': '10.0.2.1.0',
    'category': 'Generic Modules',
    'author': "GRAP,Odoo Community Association (OCA)",
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        "security/product_template_link_type.xml",
        "views/product_template_link_type.xml",
        "security/ir.model.access.csv",
        "views/action.xml",
        "views/product_template_view.xml",
        "views/product_template_link_view.xml",
        "views/menu.xml",
        "wizards/product_template_linker.xml",
    ],
    'demo': [
        "data/product_template_link_type.xml",
        "demo/product_template_link_type.xml",
        "demo/product_template_link.xml",
    ],
    'external_dependencies': {'python': ['openupgradelib']},
    'installable': True,
}
