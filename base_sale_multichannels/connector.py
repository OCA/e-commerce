# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes for OpenERP                                     #
#   Copyright (C) 2012 Camptocamp Alexandre Fayolle  <alexandre.fayolle@camptocamp.com>  #
#   Copyright (C) 2012 Akretion Sebastien Beau <sebastien.beau@akretion.com>  #
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

from base_external_referentials.connector import AbstractConnector

class BaseConnector(AbstractConnector):
    def _get_import_defaults_res_partner(self, cr, uid, context=None):
        pass
    def _get_import_defaults_res_partner(self, cr, uid, context=None):
        pass
    def _get_import_defaults_external_shop_group(self, cr, uid, context=None):
        pass

    def _get_import_defaults_sale_order(self, cr, uid, context=None):
        pass

    def _record_one_sale_order(self, cr, uid, res_obj, resource, defaults, context):
        pass
