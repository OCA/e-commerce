# Copyright 2020 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ProductPublicCategory(models.Model):
    _inherit = ["product.public.category", "website.published.mixin"]
    _name = "product.public.category"
