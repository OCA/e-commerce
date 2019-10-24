/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_secondary_unit.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    // Get an option value by its text
    // HACK https://github.com/odoo/odoo/pull/32718
    function opt_val (option_text) {
        return function (action_helper) {
            var option_id = this.$anchor.children(_.str.sprintf(
                "option:contains('%s')", option_text
            )).val();
            action_helper.text(option_id);
        };
    }

    var steps = [
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "#secondary_uom",
            run: opt_val("Box 5 Unit(s)"),
        },
        {
            trigger: "#add_to_cart",
            extra_trigger: ".js_product:has(input[name='add_qty']:propValueContains(5)):has(.price_uom)",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "span:contains(Box 5 Unit(s))"
        },
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger: ".js_product:has(input[name='add_qty']:propValueContains(1))",
        },
        {
            trigger: "a[href='/shop/checkout?express=1']",
            extra_trigger: "span:containsExact(Unit(s))"
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
