/* Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_wishlist.tour", function (require) {
    "use strict";
    var Tour = require("web.Tour");
    var base = require("web_editor.base");

    var item = "div[itemtype='http://schema.org/Product']",
        ipad = item + ":contains(iPad Mini) .js_wishlist_toggle:enabled",
        ipod = item + ":contains(iPod) .js_wishlist_toggle:enabled",
        imac = item + ":contains(iMac) .js_wishlist_toggle:enabled";

    // HACK https://github.com/odoo/odoo/issues/12961
    function workaround_12961(path, next_step) {
        return function () {
            if ((location.pathname + location.search) == path) {
                console.log(
                    "Applying workaround for " +
                    "https://github.com/odoo/odoo/issues/12961"
                );
                return next_step;
            }
        };
    }

    var tour = {
        id: "test_website_sale_wishlist",
        name: "(Un)wishlist some things, log in, save in session, log out",
        path: "/shop",
        mode: "test",
        steps: [
            {
                title: "I wish an iPod",
                element: ipod + " .fa-heart-o",
                waitFor: ipod + " .fa-heart-o",
            },
            {
                title: "I wish an iMac",
                element: imac + " .fa-heart-o",
                waitFor: ipod + " .fa-heart",
            },
            {
                title: "I want to see only what I wish",
                element: "a:has(.js_wishlist_quantity:contains(2))",
                waitFor: "a:has(.js_wishlist_quantity:contains(2))",
                onload: workaround_12961(
                    "/shop?wishlist_only=1",
                    "Well... honestly, I never wished that iPod"
                ),
            },
            {
                title: "Well... honestly, I never wished that iPod",
                element: ipod + " .fa-heart",
                waitFor: ipod + " .fa-heart",
                waitNot: item + " .fa-heart-o",
            },
            {
                title: "Let me go back to wish another thing",
                element: "a[href='/shop']",
                waitFor:
                    ipod + " .fa-heart-o, .js_wishlist_quantity:contains(1)",
                onload: workaround_12961(
                    "/shop",
                    "What I really wish is an iPad Mini"
                ),
            },
            {
                title: "What I really wish is an iPad Mini",
                element: ipad + " .fa-heart-o",
                waitFor: ipad + " .fa-heart-o",
                waitNot: ipad + " .fa-heart",
            },
            {
                title: "I go to login page",
                waitFor: ipad + " .fa-heart",
                onload: function () {
                    window.location = "/web/login?redirect=/shop";
                },
            },
            {
                title: "Fill user name and password",
                waitFor: "#login, #password",
                onload: function () {
                    // HACK Weird things happen in Travis.
                    // See https://github.com/OCA/e-commerce/pull/149
                    $(this.waitFor).val("demo")
                    .closest("form").submit();
                    return "Log in";
                },
            },
            {
                title: "Log in",
                element: "button[type=submit]",
                waitFor: "button[type=submit]",
                onload: workaround_12961(
                    "/shop",
                    "Let me check my wishlist now that I am logged in"
                ),
            },
            {
                title: "Let me check my wishlist now that I am logged in",
                element: ".js_wishlist_quantity:contains(2)",
                waitFor: ipad + " .fa-heart",
                waitNot: ipod + " .fa-heart",
                wait: 1200,
                onload: workaround_12961(
                    "/shop?wishlist_only=1",
                    "My wishlist is intact, I click on my name"
                ),
            },
            {
                title: "My wishlist is intact, I click on my name",
                element: ".dropdown-toggle:contains(Demo User)",
                waitFor:
                    imac + " .fa-heart, " + ipad + " .fa-heart, "
                    + ".js_wishlist_quantity:contains(2)",
                waitNot: ipod,
            },
            {
                title: "I log out",
                element: "a[href='/web/session/logout?redirect=/']",
                waitFor: "a[href='/web/session/logout?redirect=/']:visible",
            },
            {
                title: "No wishlist now that it is saved in my account",
                waitFor: "a[href='/web/login']",
                waitNot: ".js_wishlist_quantity:visible",
            },
        ]
    };

    // HACK https://github.com/odoo/odoo/pull/13622
    // TODO When merged, replace by animation.started.done(...)
    return base.ready().done(function () {
        return Tour.register(tour);
    });
});
