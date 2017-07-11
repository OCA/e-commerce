/* Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_wishlist.tour", function (require) {
    "use strict";
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");


    var item = "div[itemtype='http://schema.org/Product']",
        ipad = item + ":contains(iPad Mini) .js_wishlist_toggle:enabled",
        ipod = item + ":contains(iPod) .js_wishlist_toggle:enabled",
        imac = item + ":contains(iMac) .js_wishlist_toggle:enabled";


    tour.register("test_website_sale_wishlist", {
            name: "(Un)wishlist some things, log in, save in session, log out",
            test: true,
            url: "/shop",
            wait_for: base.ready()
        },
        [
            {
                content: "I wish an iPod",
                extra_trigger: ipod + " .fa-heart-o",
                trigger: ".btn.js_wishlist_toggle[data-product=18]",
                run: "click",
            },
            {
                content: "I wish an iMac",
                extra_trigger: ipod + " .fa-heart, " + imac + " .fa-heart-o",
                trigger: ".btn.js_wishlist_toggle[data-product=15]",
                run: "click",

            },
            {
                content: "I want to see only what I wish",
                extra_trigger: "a:has(.js_wishlist_quantity:contains(2))",
                trigger: "a[href='/shop?wishlist_only=1']",
                run: "click",
            },
            {
                content: "Well... honestly, I never wished that iPod",
                extra_trigger: ".active>a[href='/shop?wishlist_only=1']",
                trigger: ".btn.js_wishlist_toggle[data-product=18]",
                run: "click",
            },
            {
                content: "Let me go back to wish another thing",
                extra_trigger: ipod + " .fa-heart-o, .js_wishlist_quantity:contains(1)",
                trigger: "a[href='/shop']",
                run: "click",
            },
            {
                content: "What I really wish is an iPad Mini",
                extra_trigger: ipod + " .fa-heart-o",
                trigger: ".btn.js_wishlist_toggle[data-product=13]",
                run: "click",
            },
            {
                content: "I go to login page",
                extra_trigger: ipad + " .fa-heart",
                trigger: "a[href='/web/login']",
                run: "click",
            },
            {
                content: "Enter user name",
                trigger: "#login",
                run: "text(portal)",
            },{
                content: "Enter password",
                trigger: "#password",
                run: "text(portal)",
            },
            {
                content: "Log in",
                trigger: ".btn:contains('Log in')",
                run: "click",
            },
            {
                content: "Let me check my wishlist now that I am logged in",
                extra_trigger: ".dropdown-toggle:contains(Demo Portal User)",
                trigger: "a[href='/shop?wishlist_only=1']",
                run: "click",
            },
            {
                content: "My wishlist is intact, I click on my name",
                extra_trigger: imac + " .fa-heart, " + ipad + " .fa-heart, "
                + ".js_wishlist_quantity:contains(2)",
                trigger: ".dropdown-toggle:contains(Demo Portal User)",
                run: "click",
            },
            {
                content: "I log out",
                trigger: "a[href='/web/session/logout?redirect=/']:visible",
                run: "click",
            },
            {
                content: "No wishlist now that it is saved in my account",
                trigger: "a[href='/shop']",
                extra_trigger: "b:contains('Sign in')",
                run: "click",
            },
            {
                content: "No wishlist now that it is saved in my account",
                extra_trigger: ipod + " .fa-heart-o",
                trigger: imac + " .fa-heart-o",
            },
        ]
    );

});
