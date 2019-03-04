# -*- coding: utf-8 -*-
from openerp import api, fields, models
from psycopg2.extensions import AsIs


class IrModelFields(models.Model):

    _inherit = "ir.model.fields"

    is_filter = fields.Boolean('Show as Filter', default=False)
    is_in_description = fields.Boolean(
        'Show in website product description', default=False
    )

    # underscore methods in ORM are private, an extra security other than
    # separating code and parameters. cannot be called externally.
    def _update_special_attributes(self, base_attribute, field_vals):

        batt = base_attribute
        batt_value = field_vals[base_attribute]
        # errors would be raised by doing this via ORM, but field_vals has
        # only special attributes we know have to be modifiable
        sql = ("update ir_model_fields "
               "set %s=%s "
               "where id in %s ")
        self.env.cr.execute(
            sql, (AsIs(batt), batt_value, tuple(self.ids)))

    @api.multi
    def write(self, vals):
        field_vals = {}
        result = True
        special_attributes = ['is_filter', 'is_in_description', 'selection']
        for attribute in special_attributes:
            if attribute in vals.keys():
                field_vals[attribute] = vals.pop(attribute)
                # fetch back selection field, selection string value is not in
                # the db , because it may be calculated in many ways. keeping
                # it the same
        # if values are left in original dict, run standard write so that we
        # catch and stop execution if some forbidden operations are done on
        # base fields
        result = super(IrModelFields, self).write(vals=vals)
        # if the field is manual the ORM cannot modify it, so we will skip the
        # popup error if one of the two fields we are intrested are there
        if field_vals:
            for base_attribute in field_vals.keys():
                self._update_special_attributes(base_attribute, field_vals)
        return result
