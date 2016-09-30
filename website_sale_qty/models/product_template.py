# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_quantity_tiers = fields.Serialized(
        compute='_compute_price_quantity_tiers',
        help='Unit prices by pricelist and minimum quantity',
    )

    @api.multi
    def _compute_price_quantity_tiers(self):
        pricelists = self.env['product.pricelist'].search([('id', '>', 0)])

        for record in self:
            results = {}

            for pricelist in pricelists:
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

                list_results = set([])
                for min_qty in min_quantities:
                    res = pricelist.price_rule_get(
                        record.product_variant_ids[0].id, min_qty
                    )
                    if res[pricelist.id][1] in pricelist_items.ids:
                        list_results.add((min_qty, res[pricelist.id][0]))

                list_results = sorted(list(list_results))
                results[pricelist.id] = list_results

            record.price_quantity_tiers = results
