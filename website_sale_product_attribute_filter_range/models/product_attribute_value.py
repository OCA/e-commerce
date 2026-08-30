# Copyright 2025 EthicHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    numeric_value = fields.Float(
        digits=(12, 2),
        help="Numeric value used for range filtering on the website. "
        "Automatically computed from the value name if it contains a number.",
    )

    @api.onchange("name")
    def _onchange_name_set_numeric_value(self):
        for record in self:
            if record.name and record.attribute_id.display_type == "range":
                parsed = self._parse_numeric_value(record.name)
                if parsed is not None:
                    record.numeric_value = parsed

    @staticmethod
    def _parse_numeric_value(name):
        """Try to extract a numeric value from a string.

        Supports both dot and comma as decimal separators
        (e.g., '84.5' or '84,5').
        """
        match = re.search(r"[-+]?\d+([.,]\d+)?", name or "")
        if match:
            try:
                return float(match.group().replace(",", "."))
            except ValueError:
                return None
        return None
