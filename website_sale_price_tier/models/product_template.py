# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import json
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_quantity_tiers = fields.Serialized(
        compute='_compute_price_quantity_tiers',
        help='This is a list of minimum quantities where pricing for the'
             ' product changes, along with total costs for each of those'
             ' quantities. It is computed for the current pricelist.',
    )

    @api.multi
    def _compute_price_quantity_tiers(self):
        for record in self:
            current_website = self.env['website'].get_current_website()
            pricelist = current_website.get_current_pricelist()
            pricelist_items = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', pricelist.id),
                ('product_tmpl_id', '=', record.id),
                '|',
                ('date_start', '<=', fields.Date.today()),
                ('date_start', '=', False),
                '|',
                ('date_end', '>=', fields.Date.today()),
                ('date_end', '=', False),
            ])

            min_quantities = set([])
            for price in pricelist_items:
                min_quantities.add(
                    1 if price.min_quantity < 1 else price.min_quantity
                )
            if current_website.show_implicit_price_tier:
                min_quantities.add(1)

            list_results = set([])
            for min_qty in min_quantities:
                subtotal = record.with_context(
                    quantity=min_qty,
                ).website_price
                list_results.add((min_qty, subtotal))

            list_results = sorted(list(list_results))
            # A tier with min qty of 1 should not exist on its own
            if len(list_results) == 1 and list_results[0][0] == 1:
                list_results = []
            record.price_quantity_tiers = json.dumps(list_results)
