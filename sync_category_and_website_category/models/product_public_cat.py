# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    # compute category products is used for two reasons, first is to be able to
    # access the products of a category from the backend easily, secondly while
    # testing it is a useful consistency check on categories.

    category_products = fields.Many2many(
        comodel_name='product.template',
        inverse_name='public_categ_ids',
        string='products in public category',
    )
    internal_category_id = fields.Many2one(
        'product.category',
        ondelete='cascade'
    )


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.multi
    def _compute_category_products(self):
        for this in self:
            # Add the alternative categories provided by field categ_ids from
            # github.com/OCA/product-attribute/tree/9.0/product_multi_category
            sql = """select product_id from
                     product_categ_rel
                     where categ_id = %s
                     union
                     select id from
                     product_template
                     where categ_id = %s"""
            self.env.cr.execute(sql, (this.id, this.id))
            res = [t[0] for t in self.env.cr.fetchall()]
            this.category_products = res

    category_products = fields.One2many(
        'product.template', string='products in internal category',
        compute=_compute_category_products,
        store=False
    )
    public_category_id = fields.One2many(
        comodel_name='product.public.category',
        inverse_name='internal_category_id',
        string='Associated Public category (automatic)'
    )
    # add images to internal categories
    image = fields.Binary(
        "image", attachment=True
    )

    def sync_fields(self, vals):
        # had written this with conditions as vals.get('keyname') but does not
        # make sense , because we  need to cover the false case, at least for
        # non-mandatory fields.
        values = {}
        if 'name' in vals:
            # if you keep the name the same it will apply translations
            # automatically
            values['name'] = vals.get('name')
        if 'parent_id' in vals:
            if not vals.get('parent_id'):
                values['parent_id'] = False
            else:
                values['parent_id'] = self.env['product.category'].browse(
                    [vals.get('parent_id')]).public_category_id.id
        if 'image' in vals:
            values['image'] = vals.get('image')
        if 'sequence' in vals:
            values['sequence'] = vals.get('sequence')
        if 'product_field_ids' in vals:
            values['category_attributes'] = vals.get('product_field_ids')
        if 'published' in vals:
            values['published'] = vals.get('published')
        return values

    # Case create new category
    @api.model
    def create(self, vals):
        new_category = super(ProductCategory, self).create(vals)
        values = self.sync_fields(vals)
        if new_category:
            values['internal_category_id'] = new_category.id
        self.env['product.public.category'].create(values)
        # to increase consistency we update all sincronization of
        # associated_products.
        return new_category

    @api.multi
    def write(self, vals):
        for this in self:
            written_category = super(ProductCategory, this).write(vals)
            values = this.sync_fields(vals)
            values['internal_category_id'] = this.id
            this.public_category_id.write(values)
        return written_category

    @api.multi
    def unlink(self):  # pylint: disable=W0221
        """need unlink or a million public cats will proliferate"""
        for this in self:
            res_pub = this.public_category_id.unlink()
            res = super(ProductCategory, this).unlink()
        return res and res_pub
