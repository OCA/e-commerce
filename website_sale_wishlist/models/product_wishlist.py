# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.http import request, root


class ProductWishlist(models.Model):
    _name = "product.wishlist"
    _sql_constrains = [
        ("session_or_user_id",
         "CHECK(session IS NULL != user_id IS NULL)",
         "Need a session or user for wishlisting a product, but never both."),
        ("product_unique_session",
         "UNIQUE(product_tmpl_id, session)",
         "Duplicated wishlisted product for this session."),
        ("product_unique_user_id",
         "UNIQUE(product_tmpl_id, user_id)",
         "Duplicated wishlisted product for this user."),
    ]

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        required=True,
        ondelete="cascade",
        help="Wishlisted product.",
    )
    session = fields.Char(
        default=lambda self: self._default_session(),
        help="Website session identifier where this product was wishlisted.",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        ondelete="cascade",
        default=lambda self: self._default_user_id(),
        help="User that wishlisted this product.",
    )
    website_id = fields.Many2one(
        comodel_name="website",
        string="Website",
        required=True,
        ondelete="cascade",
        default=lambda self: self._default_website_id(),
        help="Website where the user wishlisted the product.",
    )

    @api.model
    def _default_session(self):
        """Default to current session."""
        return request.session.sid if not self._default_user_id() else False

    @api.model
    def _default_user_id(self):
        """Default to current user if it's not the website user."""
        return (self.env.user != self._default_website_id().user_id and
                self.env.user)

    @api.model
    def _default_website_id(self):
        """Default to current website."""
        return self.env["website"].get_current_website()

    @api.model
    def _join_current_user_and_session(self):
        """Assign all dangling session wishlisted products to user."""
        user_products = self.search([
            ("user_id", "=", self.env.uid),
        ]).mapped("product_tmpl_id")
        session_domain = [
            ("session", "=", request.session.sid),
            ("user_id", "=", False),
        ]
        # Remove session products already present for the user
        self.search(
            session_domain + [("product_tmpl_id", "in", user_products.ids)]) \
            .unlink()
        # Assign the rest to the user
        self.search(session_domain).write({
            "user_id": self.env.uid,
            "session": False,
        })

    @api.model
    def _garbage_collector(self):
        """Remove wishlists for unexisting sessions."""
        self.search([
            ("session", "not in", root.session_store.list()),
            ("user_id", "=", False),
        ]).unlink()

    @api.model
    def _clear_methods_cache(self):
        """Clear cache for wishlist-related methods."""
        Website = self.env["website"]
        Product = self.env["product.template"]
        Website.wishlist_product_ids.clear_cache(Website)
        Website.wishlisted_product_template_ids.clear_cache(Website)
        Product.wishlisted.clear_cache(Product)

    @api.model
    def create(self, vals):
        self._clear_methods_cache()
        return super(ProductWishlist, self).create(vals)

    @api.multi
    def unlink(self):
        self._clear_methods_cache()
        return super(ProductWishlist, self).unlink()

    @api.multi
    def write(self, vals):
        self._clear_methods_cache()
        return super(ProductWishlist, self).write(vals)
