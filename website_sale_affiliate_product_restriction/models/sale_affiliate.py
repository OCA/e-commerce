# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleAffiliate(models.Model):
    _inherit = 'sale.affiliate'

    restriction_product_tmpl_ids = fields.Many2many(
        'product.template', string='Restrict to products',
        help=('If not empty, only sales that contain at least one of these'
              ' products considered part of the affiliation.'),
        )

    def _qualified_order_lines(self):
        """ Return the order lines that:
        - are related to the affiliate
        - which order is in a non-draft state
        - which product is listed in the affiliate product restriction, if any
        """
        self.ensure_one()
        domain = [('order_id.affiliate_request_id.affiliate_id', '=', self.id),
                  ('order_id.state', '!=', 'draft'),
                  ]
        if self.restriction_product_tmpl_ids:
            ids = self.restriction_product_tmpl_ids.ids
            domain.append(('product_id.product_tmpl_id', 'in', ids))
        return self.env['sale.order.line'].search(domain)

    @api.depends('request_ids', 'request_ids.sale_ids')
    def _compute_sales_per_request(self):
        """Return a number of sales per request ratio, considering the
        restriction on sold products, if any.
        """
        for record in self:
            requests = record.request_ids
            sales_count = len(set(ol.order_id
                                  for ol in record._qualified_order_lines()))
            try:
                record.sales_per_request = (
                    float(sales_count) / float(len(requests)))
            except ZeroDivisionError:
                pass

    @api.depends('request_ids', 'request_ids.sale_ids')
    def _compute_conversion_rate(self):
        """ Return the proportion of requests that end-up with at least
        one validated sale (taking product restrictions into account).
        """
        for record in self:
            requests = record.request_ids
            conversions = set(ol.order_id.affiliate_request_id
                              for ol in record._qualified_order_lines())
            try:
                record.conversion_rate = (
                    float(len(conversions)) / float(len(requests)))
            except ZeroDivisionError:
                pass
