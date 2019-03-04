/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_secondary_unit.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('iPod')",
        },
        {
            trigger: "#secondary_uom",
            run: "text 1",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger: ".js_product:has(input[name='add_qty']:propValueContains(5))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "span:contains(Box 5 Unit(s))"
        },
        {
            trigger: "a:contains('iPod')",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger: ".js_product:has(input[name='add_qty']:propValueContains(1))",
        },
        {
            trigger: "a[href='/shop/checkout']",
            extra_trigger: "span:containsExact(Unit(s))"
        },
        {
            trigger: "a[href='/shop/confirm_order']",
        },
        {
            trigger: "#o_payment_form_pay",
            extra_trigger: "table:has(span:contains(Box 5 Unit(s)):has(span:contains(Unit(s)))"
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "table:has(span:contains(Box 5 Unit(s)):has(span:contains(Unit(s)))"
        },
    ];

    tour.register("website_sale_secondary_unit",
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
