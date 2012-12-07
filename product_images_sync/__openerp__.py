# -*- encoding: utf-8 -*-
##############################################################################
#
#    product_images_sync module for OpenERP
#    Copyright (C) 2012 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Product images synchronization',
    'version': '6.1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'description': """
        This module is a generic module that handles the synchro of product images
        between OpenERP and externals referentials such as a Magento e-commerce,
        a PrestaShop e-commerce, etc...
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'product_images_olbs',
        'base_external_referentials',
        'base_sale_multichannels',
        ],
    'init_xml': [],
    'update_xml': [
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
