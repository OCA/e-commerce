# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class Website(models.Model):
    _name = "website"
    _inherit = ["website", "sendcloud.mixin"]

    sendcloud_brand_id = fields.Many2one("sendcloud.brand")
