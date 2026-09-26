# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class UomUom(models.Model):
    _inherit = "uom.uom"

    def _is_continuous(self):
        """Return whether this is a measurable UoM (kg, L, m, ...).

        Continuous UoMs are the ones that are not based on the Unit(s) reference,
        which are countable and can't be split.
        """
        if not self:
            return False
        return not self._has_common_reference(self.env.ref("uom.product_uom_unit"))
