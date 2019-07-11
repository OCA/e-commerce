/* Copyright 2019 Sergio Teruel
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("website_sale_search_no_kept.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Customize')",
        },
        {
            trigger: "a:contains('eCommerce Categories')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: ".oe_search_box",
            run: 'text Ipad'
        },
        {
            trigger: "a:contains('Laptops')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "a:contains('Laptop Customized')",
        },
    ];
    tour.register("website_sale_search_no_kept",
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
