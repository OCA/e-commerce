# Copyright Cetmix OU 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, fields, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDeliveryDate(WebsiteSale):
    @http.route(
        "/shop/delivery_date_constraints", type="json", auth="public", website=True
    )
    def delivery_date_constraints(self, carrier_id=None, **kwargs):
        """Get delivery date constraints for the selected carrier."""
        if carrier_id:
            carrier = request.env["delivery.carrier"].sudo().browse(int(carrier_id))
            if carrier.exists():
                return carrier.get_delivery_constraints()
        return False

    @http.route("/shop/set_delivery_date", type="json", auth="public", website=True)
    def set_delivery_date(self, delivery_date=None, carrier_id=None, **kw):
        """Validate the selected delivery date."""
        if not delivery_date or not carrier_id:
            return {"valid": False, "message": _("Invalid input")}
        order = request.website.sale_get_order()
        try:
            delivery_date = fields.datetime.strptime(delivery_date, "%Y-%m-%d %H:%M")
        except Exception:
            return {"valid": False, "message": _("Invalid date format")}
        carrier = request.env["delivery.carrier"].sudo().browse(int(carrier_id))
        if not carrier.exists():
            return {"valid": False, "message": _("Invalid carrier")}
        try:
            order.set_delivery_date(delivery_date)
        except ValidationError as e:
            return {"valid": False, "message": str(e)}
        return {"valid": True}
