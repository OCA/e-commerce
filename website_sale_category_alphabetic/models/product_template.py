# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        new_record = super(ProductTemplate, self).create(vals)
        new_record._add_alpha_website_categ()
        return new_record

    @api.multi
    def _add_alpha_website_categ(self):
        base_categ = self.env.ref('website_sale_category_alphabetic.base')

        for record in self:
            first_char = record.name[0]
            if first_char.isalpha():
                categ_name = first_char.upper()
                categ_seq = ord(categ_name)
            elif first_char.isdigit():
                categ_name = '#'
                categ_seq = 0x10ffff + 1
            else:
                categ_name = '*'
                categ_seq = 0x10ffff + 2

            alpha_categ = self.env['product.public.category'].search([
                ('parent_id', '=', base_categ.id),
                ('name', '=', categ_name),
            ])
            if not alpha_categ:
                alpha_categ = self.env['product.public.category'].create({
                    'parent_id': base_categ.id,
                    'name': categ_name,
                    'sequence': categ_seq,
                })

            record.public_categ_ids = [(4, alpha_categ.id, False)]
