# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product Links',
    'version': '7.0.0',
    'category': 'Generic Modules',
    'description': """
This module adds links between products:

- cross-selling
- up-selling
- related

These types of links are common in e-commerce shops.

It can be used as a base to implement synchronisations with
e-commerce (for instance, it is used in magentoerpconnect).
    """,
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'product_links_view.xml'
    ],
    'installable': True,
    'active': False,
}
