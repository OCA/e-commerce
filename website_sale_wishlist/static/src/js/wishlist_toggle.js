/* Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_wishlist.toggle", function (require) {
    "use strict";
    var animation = require('web_editor.snippets.animation');
    var session = require('web.session');

    return animation.registry.website_sale_wishlist_toggle =
    animation.Class.extend({
        selector: ".js_wishlist_toggle",
        start: function () {
            this.$icon = this.$(".fa");
            this.$quantity = $(".js_wishlist_quantity");
            this.product_id = Number(this.$el.data("product"));
            this.$el.on("click", $.proxy(this.call_toggle, this));
        },
        call_toggle: function () {
            this.$el.prop("disabled", true);
            session.rpc("/shop/wishlist/toggle/" + this.product_id).done(
                $.proxy(this.toggle_success, this),
                $.proxy(this.toggle_failure, this)
            );
        },
        toggle_success: function (wishlisted) {
            this.$el.prop("disabled", false);
            this.$icon.toggleClass("fa-heart", wishlisted)
                      .toggleClass("fa-heart-o", !wishlisted);
            this.update_wishlist_count(wishlisted ? 1 : -1);
        },
        toggle_failure: function () {
            this.$el.prop("disabled", false);
        },
        update_wishlist_count: function (add) {
            if (!this.$quantity.length) {
                // The view could be disabled; do nothing if so
                return;
            }
            var quantity = Number(this.$quantity.text()) + add;
            this.$quantity.text(quantity);
            this.$quantity.closest("li").toggleClass("hidden", quantity == 0);
        },
    });
});
