# Copyright 2020 Algoritmun Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import route, request, Controller
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime
import re


class WebsiteSale(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        res = super(WebsiteSale, self)._get_mandatory_billing_fields()
        res.extend(['firstname', 'lastname'])
        return res

    def values_preprocess(self, order, mode, values):
        partner_fields = super(WebsiteSale, self).values_preprocess(order, mode, values)
        partner_fields['name'] = ' '.join([partner_fields.get('lastname'), partner_fields.get('firstname')])
        return partner_fields

