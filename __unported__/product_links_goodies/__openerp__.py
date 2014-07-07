# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_links_goodies for OpenERP                                  #
#   Copyright (C) 2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
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
    'name': 'product_links_goodies',
    'version': '6.1.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
        Module that add the type of link goodies (free product)
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['product_links', 'purchase'], 
    'init_xml': [],
    'update_xml': [ 
            'product_links_view.xml',
            'purchase_view.xml',
            'product_goodies_data.xml',
    ],
    'demo_xml': [],
    'installable': False,
    'active': False,
}

