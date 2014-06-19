# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele
#    Copyright 2014 Camptocamp SA
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
    'name': 'Receivable Account Payment Method',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
Receivable Account Payment Method
===================

This module adds possibility to configure
a default receivable account on a payment method:

When a default receivable account is specified on a payment method,
an invoice using this payment method uses it instead of
receivable account defined on partner.
""",
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com/',
    'depends': ['sale_payment_method',
                ],
    'data': ['account_invoice_view.xml',
             'payment_method_view.xml',
             ],
    'demo': [],
    'test': ['test/receivable_account_payment_method.yml'],
    'installable': True,
}
