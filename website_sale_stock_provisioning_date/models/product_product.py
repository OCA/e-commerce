# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_next_provisioning_date(self, company):
        domain = [
            ("company_id", "=", company.id),
            ("product_id", "in", self.ids),
            ("state", "not in", ["draft", "done", "cancel"]),
            ("location_id.usage", "=", "supplier"),
            ("location_dest_id.usage", "=", "internal"),
            ("date", ">=", fields.Datetime.now()),
        ]
        move = self.env["stock.move"].sudo().search(domain, order="date", limit=1)
        return move and move.date.date() or False
