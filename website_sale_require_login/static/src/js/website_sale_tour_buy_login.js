/* © 2015 Antiun Ingeniería S.L. - Jairo Llopis
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

"use strict";
(function ($) {
    var steps = openerp.Tour.tours.shop_buy_product.steps;

    // Gets user name from login menu (see openerp.Tour.log)
    function user() {
        return $(".navbar .dropdown:has(>.js_usermenu) a:first, " +
                 ".navbar .oe_topbar_name, " +
                 ".pos .username").text();
    }

    // Alter expected buying workflow for public users
    if (!user()) {
        for (var position = 0; position < steps.length; position++) {
            if (steps[position].title === "go to checkout") {
                steps.splice(
                    position,
                    1,
                    {
                        title: "go to checkout",
                        waitFor: "#cart_products input.js_quantity[value=1]",
                        element: "a span:contains('Log in and checkout')",
                    },
                    {
                        title: "Log in",
                        element: "form.oe_login_form button[type=submit]",
                        onload: function () {
                            $("#login").val("demo");
                            $("#password").val("demo");
                        },
                    }
                );
                break;
            }
        }
    }
})(jQuery);
