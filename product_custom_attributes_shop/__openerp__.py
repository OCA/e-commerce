# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes_shop for OpenERP                                 #
#   Copyright (C) 2012 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################



{
    'name': 'product_custom_attributes_shop',
    'version': '6.1.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
    This module give the posibility to manage different value for special field
    (like name, description, metadata....) per shop.
    Indeed when you sale on an e-shop you must have for exemple a different
    description per product (ranking problem). This that module you will be able
    to add in the shop tab of the product a description per shop.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'base_sale_multichannels',
        'product_custom_attributes',
        ],
    'init_xml': [],
    'update_xml': [
        'sale_view.xml',
        'product_attribute_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

