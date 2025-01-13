# Copyright 2025 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, format_date

from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery

_logger = logging.getLogger(__name__)


class WebsiteSaleCommitmentDate(WebsiteSaleDelivery):
    @http.route()
    def payment(self, **post):
        res = super().payment(**post)
        order = request.website.sale_get_order()
        if order and order.carrier_id:
            res.qcontext.update(
                "allow_commitment_date", order.carrier_id.allow_commitment_date
            )
        return res

    @http.route(
        "/shop/update_commitment_date", type="json", auth="public", website=True
    )
    def update_commitment_date(self, **post):
        order = request.website.sale_get_order()
        string_date = post.get("date")
        lang = request.env["res.lang"]._lang_get(
            request.env.context.get("lang", False) or request.env.user.lang
        )
        if order:
            date_obj = datetime.strptime(
                string_date,
                lang.date_format if lang else DEFAULT_SERVER_DATE_FORMAT,
            )
            order.commitment_date = date_obj
        return {
            "success": order.commitment_date.date() == date_obj.date(),
            "date": format_date(request.env, date_obj.date()),
        }

    @http.route()
    def update_eshop_carrier(self, **post):
        res = super().update_eshop_carrier(**post)
        order = request.website.sale_get_order()
        if order.carrier_id and not order.carrier_id.allow_commitment_date:
            order.commitment_date = False
        return res

    def _update_website_sale_delivery_return(self, order, **post):
        res = super()._update_website_sale_delivery_return(order, **post)
        if order and order.carrier_id:
            res["allow_commitment_date"] = order.carrier_id.allow_commitment_date
        return res

    @http.route("/calendar/commitment_date", type="json", auth="public", website=True)
    def commitment_date(self, **post):
        order = request.website.sale_get_order()
        carrier = order.carrier_id
        value = {}
        lang = request.env["res.lang"]._lang_get(
            request.env.context.get("lang", False) or request.env.user.lang
        )
        action = post.get("action", False)
        start = post.get("start", False)
        if start:
            start = datetime.strptime(
                start, lang.date_format if lang else DEFAULT_SERVER_DATE_FORMAT
            ).date()

        if carrier:
            if action == "prev":
                value = carrier._get_calendar_context(
                    start=start - relativedelta(months=1)
                )
            elif action == "next":
                value = carrier._get_calendar_context(
                    start=start + relativedelta(months=1)
                )
            else:
                value = carrier._get_calendar_context()
        return value
