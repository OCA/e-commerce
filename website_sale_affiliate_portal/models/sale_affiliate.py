# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from datetime import date
from collections import OrderedDict, defaultdict
from copy import deepcopy

from odoo import models, fields, api
from odoo.tools.translate import html_translate


class SaleAffiliate(models.Model):
    _inherit = 'sale.affiliate'

    valid_sale_states = {'sent', 'sale', 'done'}

    gain_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ], default='percentage', string='Gain per sale value type')

    gain_value = fields.Float(string="Gain per sale Value")

    partner_description = fields.Html(
        'Description for affiliate partner\'s extranet',
        sanitize_attributes=False, translate=html_translate)

    def _gain_fixed(self, amount):
        return self.gain_value

    def _gain_percentage(self, amount):
        return amount * self.gain_value / 100.

    @api.multi
    def report_data(self, month_num=None):
        """ Return monthly statistics for current (single) affiliate, in
        chronological order, for each of the last `month_num` months
        from now (if not older than the affiliate's creation date).

        The returned value is an ordered dict with keys being the
        (chronologically ordered) months and values ordered dict which
        keys are the (alphabetically ordered) products (where all
        restricted products, if any, have an entry) and values are:

        - the validated sale number
        - the financial gain of the affiliate partner

        """
        self.ensure_one()

        oldest = None
        if month_num is not None:
            oldest = (date.today().replace(day=1)
                      - relativedelta(months=month_num)
                      ).strftime(fields.DATETIME_FORMAT)

        data = {}
        prod_item = {'validated': 0, 'gain': 0.}

        month_item = {p.name: prod_item.copy()
                      for p in self.restriction_product_tmpl_ids}

        gain_func = getattr(self, '_gain_' + self.gain_type)

        for ol in self._qualified_order_lines():
            so = ol.order_id
            if oldest is not None and so.create_date < oldest:
                continue
            month = fields.Datetime.to_string(so.create_date)[:7]  # XXX month repr

            if month not in data:
                data[month] = deepcopy(month_item)
            month_data = data[month]

            prod_name = ol.product_id.product_tmpl_id.name
            if prod_name not in month_data:
                month_data[prod_name] = prod_item.copy()
            prod_data = month_data[prod_name]

            qty = int(ol.product_uom_qty)
            prod_data['validated'] += qty
            prod_data['gain'] += qty * gain_func(ol.price_unit)

        requests = defaultdict(int)
        for req in self.request_ids:
            if oldest is not None and req.create_date < oldest:
                continue
            month = fields.Datetime.to_string(req.create_date)[:7]
            requests[month] += 1
            if month not in data:
                month_data = deepcopy(month_item)
                if not month_data:
                    month_data['-'] = prod_item.copy()
                data[month] = month_data

        return OrderedDict([
            (month, OrderedDict([
                ('by-product', OrderedDict([
                    (product, data[month][product])
                    for product in sorted(data[month])])),
                ('visits', requests.get(month, 0))]))
            for month in sorted(data)])
