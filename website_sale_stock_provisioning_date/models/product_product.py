# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_next_provisioning_date(self, company):
        domain = [
            ("company_id", "=", company.id),
            ("product_id", "in", self.ids),
            ("state", "not in", ["draft", "done", "cancel"]),
            "|",
            ("location_id.usage", "=", "supplier"),
            ("move_orig_ids.location_id.usage", "=", "supplier"),
            ("location_dest_id.usage", "=", "internal"),
            ("date_provisioning", ">=", fields.Datetime.today()),
        ]
        move = (
            self.env["stock.move"]
            .sudo()
            .search(domain, order="date_provisioning", limit=1)
        )
        return move and move.date_provisioning or False
