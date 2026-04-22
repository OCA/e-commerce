from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_payment_term_by_order_id(self, order_id):
        """Get property term by order id"""
        return self.sudo().browse(order_id).partner_id.property_payment_term_id
