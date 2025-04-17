# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFee(WebsiteSale):
    @http.route()
    def shop_payment(self, **post):
        res = super().shop_payment(**post)
        order = request.website.sale_get_order()
        provider_id = post.get("provider_id")
        payment_option_id = post.get("payment_option_id")
        payment_methods_sudo = res.qcontext.get("payment_methods_sudo")
        providers_sudo = res.qcontext.get("providers_sudo")
        if payment_option_id:
            res.qcontext["selected_payment_method"] = int(payment_option_id)
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
                    res.qcontext["selected_provider"] = selected_provider
            order.sudo().update_fee_line(selected_provider.sudo())
        return res
