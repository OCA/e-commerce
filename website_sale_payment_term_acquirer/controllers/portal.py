from odoo.addons.sale.controllers import portal as sale_portal


class PaymentPortal(sale_portal.PaymentPortal):
    def _create_transaction(self, *args, **kwargs):
        sudo_transaction = super()._create_transaction(*args, **kwargs)
        acquirer = sudo_transaction.provider_id
        if not acquirer.display_main_payment_term and acquirer.payment_term_id:
            sudo_transaction.sale_order_ids.write(
                {"payment_term_id": acquirer.payment_term_id}
            )
        return sudo_transaction
