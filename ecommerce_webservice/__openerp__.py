# -*- coding: utf-8 -*-
# Copyright 2015 Julien Thewys. All rights reserved.  Use of this source
# code is governed by the GNU AGPL v>=3 found in the LICENSE file.

{
    'name': 'Ecommerce Web Services',
    'version': '7.0.0',
    'category': 'Generic Modules',
    'license': 'AGPL-3',
    'description': """
This web-service will act as a high-level proxy towards the more low-level API methods of Odoo.
""",
    'author': "Camptocamp, Odoo Community Association (OCA)",
    'depends': [
        'sale',
        'stock',
                ],
    'data': [
        'security/res.groups.csv',
        'security/ecommerce_api/ir.model.access.csv',
        'security/ecommerce_api/ecommerce_api_shop.xml',
        'security/ecommerce_api_internal/ir.model.access.csv',
        'security/ecommerce_api_internal/ecommerce_api_shop.xml',
        'security/ecommerce_api_management/ir.model.access.csv',

        'data/res_users.xml',

        'view/ecommerce_api_shop.xml',
        'view/ecommerce_api_log.xml',
             ],
    'demo': [
        'demo/res.partner.csv',
        'demo/res.users.csv',
        'demo/ecommerce.api.shop.csv',
        ],
    'installable': True,
}

