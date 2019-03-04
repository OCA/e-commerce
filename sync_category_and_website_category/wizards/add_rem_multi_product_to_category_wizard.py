# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AddRemMultProductToCategoryWizard(models.TransientModel):

    _name = "add_rem_mult_prd_wiz"
    _description = "wizard to remove/add multiple products from category"

    category_id = fields.Many2one('product.category')
    products_ids = fields.Many2many(
        'product.template',
    )
    # feedback fields
    removed = fields.Html('Removed Products')
    moved_to_all = fields.Html(
        'Of wich was main category and now is default category ALL')
    removed_extra = fields.Html(
        'Of wich was extra category')
    added_as_extra = fields.Html(
        'Added Products (this category as extra category)')

    @api.model
    def default_get(self, fields_list):
        result = {}
        result = super(AddRemMultProductToCategoryWizard, self).default_get(
            fields_list=fields_list
        )
        category_model = self.env['product.category']
        category_id = self.env.context.get("active_id", False)
        result["category_id"] = category_id
        result["products_ids"] = category_model.browse(
            category_id).category_products.ids
        return result

    @api.multi
    def rem_products_from_internal_category(self):
        """
        category_products (in product.category) is a computed field that
        aggregates products that have the current category as main and or
        as extra category, this implements the inverse logic of
        removal/addition.
        To be sure to have absolute consistency we search for the selected
        products in both fields and remove them from both.
        After that the syncing structure will take care of updating public
        too.
        """
        feedback = {
            'removed': [],
            'main_cat_moved_to_all': [],
            'removed_extra': [],
            'added_as_extra': []
        }

        removed_products = \
            self.category_id.category_products - self.products_ids
        added_products = self.products_ids - self.category_id.category_products

        for removed in removed_products:
            # we need to check if they where in extra or in main, remove both.
            if removed.categ_id == self.category_id:
                # if i remove from main category, i put it in 'all'
                removed.write({
                    'categ_id': self.env.ref('product.product_category_all').id
                })
                feedback['removed'].append(
                    (removed.name, removed.default_code))
                feedback['main_cat_moved_to_all'].append(
                    (removed.name, removed.default_code))

            if self.category_id.id in removed.categ_ids.ids:
                removed.write({'categ_ids': [(3, self.category_id.id, 0)]})
                feedback['removed'].append(
                    (removed.name, removed.default_code))
                feedback['removed_extra'].append(
                    (removed.name, removed.default_code))
        for added in added_products:
            # add as an extra category, not as main.
            added.write({'categ_ids': [(4, self.category_id.id, 0)]})
            feedback['added_as_extra'].append(
                (added.name, added.default_code))
        self.calculate_feedback(feedback)
        return {
            'name': 'feedback',
            'type': 'ir.actions.act_window',
            'res_model': 'add_rem_mult_prd_wiz',
            'view_id': self.env.ref(
                'sync_category_and_website_category.wizard_feedback').id,
            'view_mode': 'form',
            'res_id': self.id,
            'view_type': 'form',
            'target': 'new',
        }

    def calculate_feedback(self, feedback):
        if feedback['removed']:
            removed = '<h4>Removed Products</h4> <p>' + str(
                feedback['removed'] or 'None') + '</p>'
            self.write({'removed': removed})
        if feedback['main_cat_moved_to_all']:
            removed = """ <h4>Products removed from this category and
                          now placed in 'all products' </h4> """
            moved_to_all = '<p>' + str(feedback[
                'main_cat_moved_to_all'] or 'None') + '</p>'
            self.write({'moved_to all': moved_to_all})
        if feedback['removed_extra']:
            removed_extra = """<h4>Products that had this category as extra
                now removed </h4>  <p> """ + str(
                feedback['removed_extra'] or 'None') + '</p>'
            self.write({'removed_extra': removed_extra})
        if feedback['added_as_extra']:
            added_as_extra = """ <h4>Added products
                                 (as extra category) </h4> """
            added_as_extra = '<p>' + str(feedback[
                'added_as_extra'] or 'None') + '</p>'
            self.write({'added_as_extra': added_as_extra})
