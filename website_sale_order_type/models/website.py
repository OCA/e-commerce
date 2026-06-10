# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        check_company=True,
        help="If set, this sale order type is used for all orders created "
        "from this website and takes precedence over the partner sale order type.",
    )

    def _get_sale_order_type(self, partner_sudo):
        self.ensure_one()
        return self.sudo().sale_type_id or partner_sudo.sudo().sale_type

    def _prepare_sale_order_values(self, partner_sudo):
        self.ensure_one()
        so_data = super()._prepare_sale_order_values(partner_sudo)

        sale_type = self._get_sale_order_type(partner_sudo)
        if sale_type:
            so_data["type_id"] = sale_type.id
            if sale_type.payment_term_id:
                so_data["payment_term_id"] = sale_type.payment_term_id.id
        return so_data

    def get_pricelist_available(self, show_visible=False):
        website = self.with_company(self.company_id)
        partner_sudo = website.env.user.partner_id
        pricelists = super().get_pricelist_available(show_visible)
        sale_type = website._get_sale_order_type(partner_sudo)
        if sale_type.pricelist_id:
            pricelists = pricelists.filtered(
                lambda pricelist: pricelist.id == sale_type.pricelist_id.id
            )
        return pricelists
