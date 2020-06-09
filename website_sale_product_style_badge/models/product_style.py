# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import time
from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slug


class ProductStyle(models.Model):
    _inherit = "product.style"

    html_content = fields.Text(
        string="HTML Content",
        default="<span role='button' class='badge badge-primary'>"
                "$style_name</span>",
        groups="base.group_system")

    @api.onchange('name')
    def _onchange_name(self):
        self.html_class = "product-badge-%s" % slug(
            (time.time()*1000, self.name))
