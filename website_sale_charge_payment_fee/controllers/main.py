# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFee(WebsiteSale):
    @http.route(
        "/shop/payment", type="http", auth="public", website=True, sitemap=False
    )
    def shop_payment(self, **post):
        order = request.website.sudo().sale_get_order()
        render_values = self._get_shop_payment_values(order, **post)
        provider_id = post.get("provider_id")
        payment_option_id = post.get("payment_option_id")
        payment_methods_sudo = render_values.get("payment_methods_sudo")
        providers_sudo = render_values.get("providers_sudo")
        selected_provider = False
        if provider_id or providers_sudo:
            if provider_id:
                selected_provider = request.env["payment.provider"].browse(
                    int(provider_id)
                )
            else:
                _selected_provider = [
                    provider_sudo
                    for provider_sudo in payment_methods_sudo.provider_ids
                    if provider_sudo in providers_sudo
                ][:1]
                if len(_selected_provider) > 0:
                    selected_provider = _selected_provider[0]
            order.sudo().update_fee_line(selected_provider.sudo())
        res = super().shop_payment(**post)
        if payment_option_id:
            res.qcontext["selected_payment_method"] = int(payment_option_id)
        if selected_provider:
            res.qcontext["selected_provider"] = selected_provider
        return res
