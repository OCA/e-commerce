# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product links',
    'version': '1.0',
    'category': 'Generic Modules/Products',
    'description': """
This module adds links between products :
 - cross-selling
 - up-selling
 - related
These types of links are common in e-commerce shops.

It can be used as a base to implement synchronisations with e-commerce (used in magentoerpconnect).
    """,
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['base','product'],
    'init_xml': [],
    'update_xml': [
                   'security/ir.model.access.csv',
                   'product_links_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
