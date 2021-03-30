# Copyright 2020 Algoritmun Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import route, request, Controller
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime


class CustomerPortal(CustomerPortal):

    CustomerPortal.MANDATORY_BILLING_FIELDS.extend(['firstname', 'lastname'])

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if post.get('firstname') or post.get('lastname'):
            post['name'] = ' '.join([post.get('lastname'), post.get('firstname')])
        return super(CustomerPortal, self).account(redirect, **post)
