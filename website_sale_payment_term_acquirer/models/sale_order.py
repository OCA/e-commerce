from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_payment_term_by_order_id(self, order_id):
        """Get property term by order id"""
        return self.sudo().browse(order_id).partner_id.property_payment_term_id

    def _create_payment_transaction(self, vals):
        transactions = super()._create_payment_transaction(vals)
        for transaction in transactions:
            acquirer = transaction.acquirer_id
            if not acquirer.display_main_payment_term and acquirer.payment_term_id:
                transaction.sale_order_ids.write(
                    {"payment_term_id": acquirer.payment_term_id}
                )
        return transactions
