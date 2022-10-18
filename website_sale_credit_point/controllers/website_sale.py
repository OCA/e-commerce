# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def checkout_redirection(self, order):
        """Don't process checkout if credit check is not satisfied."""
        redirection = super(WebsiteSale, self).checkout_redirection(order)
        if redirection:
            return redirection
        else:
            try:
                order.credit_point_check()
            except UserError as exc:
                # error msg if not enought points
                request.session["credit_point_limit_error"] = exc.name
                return request.redirect("/shop/cart/")
