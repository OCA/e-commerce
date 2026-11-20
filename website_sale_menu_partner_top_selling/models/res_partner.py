# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models
from odoo.fields import Domain


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_my_regular_products_since(self):
        """Return the earliest order date to count, or None for all orders."""
        days = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale_menu_partner_top_selling.period_days")
        )
        try:
            days = int(days or 0)
        except (TypeError, ValueError):
            days = 0
        if days > 0:
            return fields.Date.today() - timedelta(days=days)
        return None

    def _get_my_regular_products_quantities(self):
        """Return the quantity of products this partner regularly buys.

        The result maps ``product.template`` ids to the total ordered
        quantity on confirmed sales orders of this partner's commercial
        partner. Other modules (e.g. Point of Sale) can extend this method
        to add their own sources.
        """
        self.ensure_one()
        partner = self.sudo().commercial_partner_id or self
        domain = [
            (
                "order_id.partner_id.commercial_partner_id",
                "=",
                partner.id,
            ),
            ("order_id.state", "in", ["sale", "done"]),
        ]
        since = self._get_my_regular_products_since()
        if since:
            domain.append(("order_id.date_order", ">=", since))
        product_data = (
            self.env["sale.order.line"]
            .sudo()
            ._read_group(
                domain=domain,
                groupby=["product_id.product_tmpl_id"],
                aggregates=["product_uom_qty:sum"],
            )
        )
        return {template.id: qty for template, qty in product_data if qty > 0}

    def _get_my_regular_products(self, website):
        """Return the shop-visible templates bought by this partner.

        The recordset is sorted by purchased quantity, descending.
        """
        self.ensure_one()
        quantities = self._get_my_regular_products_quantities()
        if not quantities:
            return self.env["product.template"]
        domain = website.sale_product_domain() & Domain("id", "in", list(quantities))
        templates = self.env["product.template"].sudo().search(domain)
        sorted_templates = templates.sorted(
            key=lambda template: quantities.get(template.id, 0), reverse=True
        )
        limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale_menu_partner_top_selling.limit", 10)
        )
        return self.env["product.template"].browse(
            template.id for template in sorted_templates[:limit]
        )
