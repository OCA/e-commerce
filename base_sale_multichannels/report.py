# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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

from osv import osv, fields
from tools.translate import _


class external_report(osv.osv):
    _inherit = 'external.report'

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True),
        }

    def get_report_by_ref(self, cr, uid, ref, external_referential_id,
                          context=None):

        report_id = False
        report = self.search(cr, uid,
                           [('ref', '=', ref),
                            ('external_referential_id',
                             '=', external_referential_id),
                            ('shop_id', '=', context.get('shop_id', False))],
                           context=context)
        if report:
            report_id = report[0]

        return report_id

    def end_report(self, cr, uid, id, context=None):
        report_id = super(external_report, self).\
        end_report(cr, uid, id, context)
        if context.get('shop_id', False):
            self.write(cr, uid, report_id,
                       {'shop_id': context['shop_id']},
                       context)
        return id

external_report()
