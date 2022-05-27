# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleSecondaryUnit(WebsiteSale):
    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        # Add secondary uom info to session
        request.session.pop("secondary_uom_id", None)
        if kw.get("secondary_uom_id"):
            secondary_uom = request.env["product.secondary.unit"].browse(
                int(kw["secondary_uom_id"])
            )
            request.session["secondary_uom_id"] = secondary_uom.id
        return super().cart_update(product_id, add_qty=add_qty, set_qty=set_qty, **kw)

    @http.route()
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw
    ):
        so_line = request.env["sale.order.line"].browse(line_id)
        request.session.pop("secondary_uom_id", None)
        if kw.get("secondary_uom_id"):
            secondary_uom = request.env["product.secondary.unit"].browse(
                int(kw["secondary_uom_id"])
            )
            request.session["secondary_uom_id"] = secondary_uom.id
        if so_line.sudo().secondary_uom_id:
            request.session["secondary_uom_id"] = so_line.sudo().secondary_uom_id.id
        return super().cart_update_json(
            product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            display=display,
            **kw,
        )

    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super()._prepare_product_values(product, category, search, **kwargs)
        res["secondary_uom_ids"] = product.secondary_uom_ids.filtered(
            lambda su: su.active and su.is_published
        )
        return res
