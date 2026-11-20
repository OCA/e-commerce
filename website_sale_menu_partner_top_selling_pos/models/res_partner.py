# Copyright 2026 Daniel Reis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_my_regular_products_quantities(self):
        quantities = super()._get_my_regular_products_quantities()
        partner = self.sudo().commercial_partner_id or self
        domain = [
            (
                "order_id.partner_id.commercial_partner_id",
                "=",
                partner.id,
            ),
            ("order_id.state", "in", ["paid", "done", "invoiced"]),
            # Lines settling a sales order are already counted
            # through the sales order itself.
            ("sale_order_line_id", "=", False),
        ]
        since = self._get_my_regular_products_since()
        if since:
            domain.append(("order_id.date_order", ">=", since))
        pos_data = (
            self.env["pos.order.line"]
            .sudo()
            ._read_group(
                domain=domain,
                groupby=["product_id.product_tmpl_id"],
                aggregates=["qty:sum"],
            )
        )
        for template, qty in pos_data:
            quantities[template.id] = quantities.get(template.id, 0) + qty
        return {template_id: qty for template_id, qty in quantities.items() if qty > 0}
