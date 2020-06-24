/* Copyright 2020 Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_wishlist_keep.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "section:has(a:contains('Test Product')) .o_add_wishlist",
        },
        {
            trigger: "a[href='/shop/wishlist']",
        },
        {
            trigger: ".o_wish_add",
        },
        {
            trigger: "#b2b_wish",
            extra_trigger: "a:contains('Test Product')",
        },
        {
            trigger: ".o_wish_add",
        },
        {
            trigger: "a:contains('Test Product')",
            extra_trigger: "span:contains('Process Checkout')",
        },
    ];
    tour.register("website_sale_wishlist_keep",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        steps
    );
    return {
        steps: steps,
    };
});
