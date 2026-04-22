from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        values = super()._get_shop_payment_values(order, **kwargs)
        # Get Customer Payment Term
        user_payment_term = request.env.user.partner_id.property_payment_term_id
        if not user_payment_term:
            # Skip acquirers with active 'display_main_payment_term' key
            values.update(
                providers_sudo=values.get(
                    "providers_sudo", request.env["payment.provider"].sudo().browse()
                ).filtered(
                    lambda acq: not acq.display_main_payment_term,
                )
            )
        return values
