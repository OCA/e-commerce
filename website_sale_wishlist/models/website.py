# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models, tools
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    @api.multi
    @tools.ormcache("self.ids", "self.env.uid",
                    "self.env.user.current_session")
    def wishlist_product_ids(self):
        """Get wishlisted products for current session.

        :return list:
            List of IDs. Not returning records because they could lead to
            errors if you try to browse them when loaded from cache and cached
            ones used a cursor that is now closed.
        """
        domain = [("website_id", "=", self.id)]
        if self.env.user != self.user_id:
            domain += ["|", ("user_id", "=", self.env.uid)]
        domain.append(("session", "=", request.session.sid))
        return [record["id"] for record in
                self.env["product.wishlist"].search_read(domain, ["id"])]

    @api.multi
    @tools.ormcache("self.ids", "self.env.uid",
                    "self.env.user.current_session")
    def wishlisted_product_template_ids(self):
        """Get ``product.template`` records wishlisted in current session.

        :return list:
            List of IDs. Not returning records because they could lead to
            errors if you try to browse them when loaded from cache and cached
            ones used a cursor that is now closed.
        """
        wishlisted = self.env["product.wishlist"].search_read(
            [("id", "in", self.wishlist_product_ids())],
            ["product_tmpl_id"])
        return [record["product_tmpl_id"][0] for record in wishlisted]
