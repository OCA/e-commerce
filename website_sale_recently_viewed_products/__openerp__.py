# -*- coding: utf-8 -*-
##############################################################################
#
#     Copyright (c) Leonardo Donelli@ MONK Software http://www.monksoftware.it
#
#     This is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     This is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with web_expand_dialog.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Recently Viewed Products',
    'summary': (
        'Let the users keep track of the products they saw on the ecommerce'),
    'author': "MONK Software,Odoo Community Association (OCA)",
    'website': "http://www.monksoftware.it",
    'category': 'Website',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'templates/website.xml',
        'templates/website_sale.xml',
        'templates/website_sale_recently_viewed_products.xml',
    ],
}
