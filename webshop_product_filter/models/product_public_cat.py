# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    """
    in order to avoid problems when filtering,
    we can exclude on the model level all types of fields that
    don't make sense in a search:

    available field types:
        reference , datetime ,  many2many , text
        monetary, selection, float,  binary,   one2many
        char,  html, many2one ,  date ,   boolean, integer

    types that don't really make sense in a websearch:

        reference, binary, html?

    """
    # MAKING A WHITELIST, more secure.
    included_field_types = [
        'char', 'text', 'boolean',
        'selection', 'monetary', 'float',
        'integer', 'many2one', 'one2many', 'many2many',
        'datetime', 'date']
    category_attributes = fields.Many2many(
        comodel_name='ir.model.fields',
        string='categories',
        domain=lambda self: [
            ('model', '=', 'product.template'),
            ('ttype', 'in', self.included_field_types)
        ]
    )
