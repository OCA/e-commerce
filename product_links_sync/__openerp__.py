# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_links_sync for OpenERP                                            #
#   Copyright (C) 2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
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
    'name': 'product_links_sync',
    'version': '6.1.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
        Abstract Module that add generic method to syncronise product link from the sale shop
        This module is used in magentoerpconnect and will be use soon in other e-commmerce
        connector.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['base_sale_export_product', 'product_links'], 
    'init_xml': [],
    'update_xml': [ 
           'sale_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

