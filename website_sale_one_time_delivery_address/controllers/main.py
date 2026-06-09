# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleOneTimeDeliveryAddress(WebsiteSale):
    def _prepare_checkout_page_values(self, order_sudo, **kwargs):
        result = super()._prepare_checkout_page_values(order_sudo, **kwargs)
        result["one_time_delivery"] = order_sudo.one_time_delivery
        return result

    @route("/shop/update_address", type="jsonrpc", auth="public", website=True)
    def shop_update_address(self, partner_id, address_type="billing", **kw):
        """Keep one_time_delivery in sync with the selected delivery partner.

        Selecting a delivery address that is a one_time_delivery contact puts the
        order in one-time mode (billing must stay on the reseller); selecting any
        other delivery address leaves one-time mode. The parent security check
        excludes one_time_delivery contacts from the allowed children, so for
        those we validate ownership and set the shipping partner directly.
        """
        order_sudo = request.cart
        if order_sudo and address_type == "delivery":
            ResPartner = request.env["res.partner"].sudo()
            partner_sudo = ResPartner.browse(int(partner_id)).exists()
            if partner_sudo.type == "one_time_delivery":
                if (
                    not order_sudo.allow_dropship
                    or partner_sudo.commercial_partner_id
                    != order_sudo.partner_id.commercial_partner_id
                ):
                    raise Forbidden()
                order_sudo.one_time_delivery = True
                if partner_sudo != order_sudo.partner_shipping_id:
                    order_sudo._update_address(partner_sudo.id, {"partner_shipping_id"})
                return
            order_sudo.one_time_delivery = False
        return super().shop_update_address(partner_id, address_type=address_type, **kw)

    @route(
        "/shop/address/submit",
        type="http",
        methods=["POST"],
        auth="public",
        website=True,
        sitemap=False,
    )
    def shop_address_submit(
        self,
        partner_id=None,
        address_type="billing",
        use_delivery_as_billing=None,
        callback=None,
        **form_data,
    ):
        """Override to enforce billing-stays-reseller when one_time_delivery is active.

        When the order has one_time_delivery=True and a delivery address is being
        submitted, we force use_delivery_as_billing=None so that:
        - portal never sets type='other'
        - partner_invoice_id is never updated by the parent logic
        """
        order_sudo = request.cart
        if order_sudo and order_sudo.one_time_delivery and address_type == "delivery":
            use_delivery_as_billing = None
        return super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            **form_data,
        )

    def _complete_address_values(
        self,
        address_values,
        address_type,
        use_delivery_as_billing,
        *args,
        order_sudo=False,
        **kwargs,
    ):
        result = super()._complete_address_values(
            address_values,
            address_type,
            use_delivery_as_billing,
            *args,
            order_sudo=order_sudo,
            **kwargs,
        )
        # After all parent logic has set the type, override it to one_time_delivery
        # when the order is in one-time delivery mode and we are creating
        # a delivery address. use_delivery_as_billing is already stripped
        # to None by shop_address_submit, so
        # this check is safe to run unconditionally for delivery addresses.
        if address_type == "delivery" and order_sudo and order_sudo.one_time_delivery:
            address_values["type"] = "one_time_delivery"
        return result

    @route(
        "/shop/update_one_time_delivery",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def shop_update_one_time_delivery(self, one_time_delivery=False, **kwargs):
        """Toggle one-time delivery mode on the current cart.

        The mode can only be enabled for customers that allow drop-shipping;
        for any other customer the flag is forced to False, regardless of what
        the request asks for.
        """
        order_sudo = request.cart
        if not order_sudo:
            return {}
        order_sudo.one_time_delivery = (
            bool(one_time_delivery) and order_sudo.allow_dropship
        )
        return {}
