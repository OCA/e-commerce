# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from datetime import timedelta

from odoo import api, fields, models
from odoo.http import request


class AffiliateRequest(models.Model):
    _name = 'sale.affiliate.request'
    _order = 'create_date desc'

    name = fields.Char(required=True, index=True)
    affiliate_id = fields.Many2one(
        'sale.affiliate',
        string='Affiliate',
        required=True,
        help='Affiliate that referred request',
    )
    date = fields.Datetime(
        required=True,
        default=lambda self: fields.Datetime.now(),
        help='Date and time of initial request',
    )
    ip = fields.Char(
        string='Client IP',
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            'REMOTE_ADDR',
        ),
    )
    referrer = fields.Char(
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            'HTTP_REFERER',
        ),
        help='Request session referrer header',
    )
    user_agent = fields.Char(
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            'HTTP_USER_AGENT',
        ),
        help='Request session user agent',
    )
    accept_language = fields.Char(
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            'HTTP_ACCEPT_LANGUAGE',
        ),
        help='Request session accept language',
    )
    sale_ids = fields.One2many(
        'sale.order',
        'affiliate_request_id',
        string='Sales',
        help='Qualified conversions generated as a result of affiliate request'
    )

    @api.model
    def create_from_session(self, affiliate):
        try:
            name = request.session['affiliate_key']
        except KeyError:
            name = affiliate.sequence_id.next_by_id()
        return self.create({'name': name, 'affiliate_id': affiliate.id})

    @api.model_cr_context
    def find_from_session(self, affiliate):
        """Find affiliate request record based on session contents"""
        try:
            affiliate_key = request.session['affiliate_key']
            return self.search([
                ('affiliate_id', '=', affiliate.id),
                ('name', '=', affiliate_key),
            ], limit=1)
        except KeyError:
            return

    @api.multi
    def conversions_qualify(self):
        self.ensure_one()

        valid_hours = self.affiliate_id.valid_hours
        valid_sales = self.affiliate_id.valid_sales
        datetime_start = fields.Datetime.from_string(self.date)
        datetime_delta = timedelta(hours=valid_hours)
        expiration = fields.Datetime.to_string(datetime_start + datetime_delta)

        qualified_sales = valid_sales < 0 or len(self.sale_ids) < valid_sales
        qualified_time = valid_hours < 0 or fields.Datetime.now() < expiration

        return qualified_sales and qualified_time
