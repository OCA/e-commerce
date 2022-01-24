/* Copyright 2022 Tecnativa - Carlos Roca
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_cart_no_redirect.tour_redirect", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Test Product 1')",
        },
        {
            trigger: "a#add_to_cart",
        },
        {
            trigger: "h4:contains('Order Total')",
        },
    ];

    tour.register(
        "add_to_cart_redirect",
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
