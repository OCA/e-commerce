# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cart_expire_date = fields.Datetime(
        compute="_compute_cart_expire_date",
        help="Technical field: The date this cart will automatically expire",
    )

    @api.depends("write_date", "website_id.cart_expire_delay")
    def _compute_cart_expire_date(self):
        for rec in self:
            if rec.state in ["draft", "sent"] and rec.website_id.cart_expire_delay > 0:
                # In case of draft records, use current date
                from_date = rec.write_date or fields.Datetime.now()
                expire_delta = timedelta(hours=rec.website_id.cart_expire_delay)
                rec.cart_expire_date = from_date + expire_delta
            elif rec.cart_expire_date:
                rec.cart_expire_date = False
