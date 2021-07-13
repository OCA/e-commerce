# Copyright 2021 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleCouponProgram(models.Model):
    _name = "sale.coupon.program"
    _inherit = ["sale.coupon.program", "image.mixin", "website.published.mixin"]

    public_name = fields.Char(
        string="Public Name",
        help="Name of the promo showed on website bellow the banner image.",
    )
