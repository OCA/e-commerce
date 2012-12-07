# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_sale_report_synchronizer for OpenERP                                 #
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
    'name': 'base_sale_report_synchronizer',
    'version': '6.1.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
        Abstract module to syncronize invoice and refund
        report with external e-commerce system
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'base_sale_multichannels',
        'report_synchronizer',
        ], 
    'init_xml': [],
    'update_xml': [ 
            'sale_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

