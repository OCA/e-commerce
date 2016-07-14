# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    google_product_category_ids = fields.Many2many(
        string='Categories',
        comodel_name='google_product_category',
        relation='product_tmpl2google_product_category',
        column1='product_tmpl_id',
        column2='google_product_category_id')

    google_color_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Color attribute',
        help='Fill this field only for apparel items with color attribute.')

    google_size_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Size attribute',
        help='Fill this field only for apparel items with size attribute.')

    google_material_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Material attribute',
        help='Fill this field only for apparel items with material attribute.')

    google_pattern_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Pattern attribute',
        help='Fill this field only for apparel items with pattern attribute.')

    google_condition = fields.Selection(
        selection=[
            ('new', 'New'),
            ('refurbished', 'Refurbished'),
            ('used', 'Used')],
        string='Condition',
        default='new')

    google_gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('unisex', 'Unisex')],
        string='Gender')

    google_age_group = fields.Selection(
        selection=[
            ('newborn', 'Newborn'),
            ('infant', 'Infant'),
            ('toddler', 'Toddler'),
            ('kids', 'Kids'),
            ('adult', 'Adult')],
        string='Age group')

    google_mpn = fields.Char(
        string='Manufacturer part number')
