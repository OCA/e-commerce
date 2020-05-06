# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import safe_eval
from odoo import api, fields, models
from lxml import etree
from odoo.osv import orm


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inventory_availability = fields.Selection(selection_add=[
        ('custom_block',
         'Block sales on website and display a message custom'),
    ])

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """The purpose of this is to write a invisible key on field attributes
         respecting other invisible keys on this field.
         There is a PR (https://github.com/odoo/odoo/pull/26607) to odoo for
         avoiding this. If merged, remove this method and add the attribute
         in the field.
         """
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == 'form':
            view_xml = etree.XML(res['arch'])
            xml_field = view_xml.xpath("//field[@name='custom_message']")
            if xml_field:
                field = xml_field[0]
                attribs = safe_eval(field.attrib.get("attrs", "{}"))
                domain = attribs['invisible']
                inventory_tuple = next(filter(
                    lambda p: p[0] == 'inventory_availability', domain), None)
                if inventory_tuple[1] == '!=':
                    index = domain.index(inventory_tuple)
                    inventory_tuple = ('inventory_availability',
                                       'not in', [inventory_tuple[2]])
                    domain[index] = inventory_tuple
                inventory_tuple[2].append('custom_block')
                field.attrib['attrs'] = str(attribs)
                orm.setup_modifiers(field)
                res['arch'] = etree.tostring(view_xml)
        return res
