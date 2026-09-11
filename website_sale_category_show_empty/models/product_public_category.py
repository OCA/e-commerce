# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    show_when_empty = fields.Boolean(
        help="Let public and portal visitors open this category's page even "
        "when neither the category nor its children hold a published "
        "product. Without this, the page answers 404.",
    )
