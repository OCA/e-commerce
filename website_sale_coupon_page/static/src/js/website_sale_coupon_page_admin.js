/* Copyright 2020 Jairo Llopis - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("website_sale_coupon_page.tour_admin", function(require) {
    "use strict";

    const tour = require("web_tour.tour");
    const base = require("web_editor.base");

    tour.register(
        "website_sale_coupon_page_admin",
        {
            url: "/promotions",
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                trigger:
                    ".card:has(.card-body:has(.card-text:contains('10% discount')))",
                extra_trigger:
                    ".card:has(.card-body:has(.card-text:contains('10% discount'))) .card-img-top",
            },
            {
                trigger: "button:has(span:has(i.fa-times))",
                extra_trigger: ".show:has(.modal-body:has(img))",
            },
            {
                trigger:
                    ".card:has(.card-body:has(.card-text:contains('10% discount just for admin')))",
                extra_trigger:
                    ".card:has(.card-body:has(.card-text:contains('10% discount just for admin'))):not(:has(.card-img-top))",
            },
        ]
    );
});
