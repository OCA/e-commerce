/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_available_display.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var rpc = require("web.rpc");

    var steps = [
        {
            trigger: "a:contains('Computer Motherboard')",
            run: function(actions){
                    rpc.query({
                        model: 'res.partner',
                        method: 'write',
                        args: [[3], {'vat': false}]})
                        .then(function(data){
                            actions.auto();
                        })
                    }
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger: ".availability_messages:has(span:contains('0 Unit(s) in stock')):has(div:contains('Available in 10 days'))",
        },
        {
            trigger: "a[href='/shop/checkout']",
            extra_trigger: ".availability_messages:has(span:contains('0 Unit(s) in stock'))",
        },
        // To compatibility with website_sale_vat_required
        {
            trigger: "div.div_vat input[name='vat']",
            run: function(actions){
                $('div.div_vat input[name="vat"]').val("BE0477472701");
                $('#div_phone input').val('11111111');
                $('div input[name="accepted_legal_terms"]').prop( "checked", true );
            },
        },
        {
            trigger: ".btn-primary:contains('Next')",
        },
        {
            trigger: "a[href='/shop/confirm_order']",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".availability_messages:has(span:contains('0 Unit(s) in stock'))",
        },
        {
            trigger: "a:contains('Special Mouse')",
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger: ".availability_messages:has(span:contains('10 Unit(s) in stock'))",
        },
        {
            trigger: "a[href='/shop/checkout']",
            extra_trigger: ".availability_messages:has(span:contains('10.0 Unit(s) in stock'))",
        },
        {
            trigger: "a[href='/shop/confirm_order']",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".availability_messages:has(span:contains('10.0 Unit(s) in stock'))",
        },
    ];
    tour.register("website_sale_stock_available_display",
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
