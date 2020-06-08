# Copyright 2020 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import html_translate


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    website_description = fields.Html(
        sanitize_attributes=False, translate=html_translate
    )
