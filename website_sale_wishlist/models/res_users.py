# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.http import request


class ResUsers(models.Model):
    _inherit = "res.users"

    current_session = fields.Char(compute="_compute_current_session")

    @api.multi
    def _compute_current_session(self):
        """Know current session for this user."""
        try:
            sid = request.session.sid
        except (AttributeError, RuntimeError):
            sid = False
        for one in self:
            one.current_session = sid

    @api.model
    def check_credentials(self, password):
        """Make all this session's wishlists belong to its owner user."""
        result = super(ResUsers, self).check_credentials(password)
        try:
            self.env["product.wishlist"]._join_current_user_and_session()
        except RuntimeError:
            pass
        return result
