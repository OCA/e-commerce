# Copyright 2020 Algoritmun Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    firstname = fields.Char(string='Firstname',)
    lastname = fields.Char(string='Lastname',)

    @api.model
    def create(self, values):
        if values.get('firstname') or values.get('lastname'):
            name = ' '.join([values.get('lastname'), values.get('firstname')])
            if values.get('name') and name != values.get('name'):
                raise UserError(_('Firstname and lastname do not match given name.'))
            values['name'] = name
        return super(ResPartner, self).create(values)

    def write(self, values):
        res = super(ResPartner, self).write(values)

        if len(self) == 1:
            if values.get('firstname') or values.get('lastname'):
                name = ' '.join([values.get('lastname'), values.get('firstname')])
                if values.get('name') and name != values.get('name'):
                    raise UserError(_('Firstname and lastname do not match given name.'))
                values['name'] = name

        return res
