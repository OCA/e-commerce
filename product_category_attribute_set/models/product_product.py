# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models, osv, _
from lxml import etree


def view_get_insert_extra(self, view_id, view_type, res):
    """
    dynamically add tab with extra fields and
    the extra fields of the category in view.
    called by fields view get of both p.t. and p.p
    """
    if (view_type == 'form') and ('notebook' in res['arch']):
        eview = etree.fromstring(res['arch'])
        notebook = eview.xpath("//notebook")
        if not notebook:
            return res
        notebook = notebook[0]
        # so first, I implemented it in a way that the code moves fields
        # to one page called shared if it sits in multiple categories
        # but that's the case with all fields, so better have one page
        shared_fields_page = etree.SubElement(
            notebook, 'page', {'string': _('Category Attributes')})
        shared_fields_group = etree.SubElement(
            shared_fields_page, 'group')
        existing_fields = {}
        field2category = {}
        all_categories = self.env['product.category'].search([])

        # Cannot scan all 202 categories and create the nodes
        # bad perfoermance hit inserting 1 page and then filtering
        # the fields. Also faster to test.

        for mag_category in all_categories:
            product_field_ids_prd = [
                x for x in mag_category.product_field_ids
                if x.name in self._fields.keys()
            ]
            for mag_field in product_field_ids_prd:
                # don't add fields that were added by some view
                if mag_field.name not in existing_fields and\
                   eview.xpath('//field[@name="%s"]' % mag_field.name):
                    continue
                if mag_field.name in existing_fields:
                    field2category[mag_field.name].append(
                        mag_category.id)
                    continue
                existing_fields[mag_field.name] = etree.SubElement(
                    shared_fields_group, 'field', {'name': mag_field.name})
                field2category[mag_field.name] = [
                    mag_category.id]
        for field in existing_fields.values():
            # add extra categories to this too.
            field.attrib['attrs'] =\
                '{"invisible": [("categ_id", "not in", [%s]), '\
                '("categ_ids", "not in", [%s])]}' % (
                    ','.join(map(str, field2category[field.get('name')])),
                    ','.join(map(str, field2category[field.get('name')])), )
            osv.orm.setup_modifiers(field)
        res['arch'] = etree.tostring(eview)
        # postprocess returns a tuple (arch, fields)
        res_fields = self.env['ir.ui.view'].postprocess_and_fields(
            model=str(self._model), node=eview, view_id=view_id)
        for key, value in res_fields[1].iteritems():
            if str(key) in existing_fields.keys():
                res['fields'][key] = value
    return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        # pylint: disable=W0221,E1120
        res_original = super(ProductProduct, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu
        )
        res = view_get_insert_extra(
            self, view_id=view_id, view_type=view_type, res=res_original)
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        # pylint: disable=W0221,E1120
        res_original = super(ProductTemplate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu
        )
        res = view_get_insert_extra(
            self, view_id=view_id, view_type=view_type, res=res_original)
        return res
