# -*- coding: utf-8 -*-
# Python source code encoding : https://www.python.org/dev/peps/pep-0263/
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2015 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Antonio Espinosa <antonioea@antiun.com>
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

from openerp.http import request
from openerp import SUPERUSER_ID
import openerp.addons.website_sale.controllers.main as main


class WebsiteSale(main.website_sale):

    def checkout_form_validate(self, data):
        res = super(WebsiteSale, self).checkout_form_validate(data)
        cr, context = request.cr, request.context
        partner_orm = request.registry['res.partner']
        partner = partner_orm.search(cr, SUPERUSER_ID, [('email', '=',
                                     data['email'])], context=context)
        if partner:
            res['email'] = 'error'
        return res
