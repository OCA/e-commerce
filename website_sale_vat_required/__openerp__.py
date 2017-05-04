# -*- coding: utf-8 -*-
# Copyright 2015 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'e-commerce required VAT',
    'summary': 'VAT number required in checkout form',
    'version': '9.0.1.0.0',
    'category': 'Website',
    'author': "Agile Business Group, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'website_sale',
        'base_vat',
    ],
    'demo': [
        'demo/assets.xml',
    ],
    'installable': True,
    'auto_install': False,
}
