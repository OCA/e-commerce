/* © 2015 Antiun Ingeniería S.L. - Jairo Llopis
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('website_sale_require_login.tour', function(require) {

    "use strict";

    require("website_sale.tour");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var steps = tour.tours.shop_buy_product.steps;

    // Gets user name from login menu (see openerp.Tour.log)
    function user() {
        return $(".navbar .dropdown:has(>.js_usermenu) a:first, " +
                 ".navbar .oe_topbar_name, " +
                 ".pos .username").text();
    }

    for (var position = 0; position < steps.length; position++) {
        if (steps[position].content === "go to checkout") {
            if (user()) {
                // if user is authenticated -- add extra dummy step to don't break current_step counter
                steps.splice(
                    position,
                    0,
                    {
                        title: 'dummy',
                        auto: 1,
                        trigger: "footer :contains(Copyright)"
                    }
                );
            } else {
                // Alter expected buying workflow for public users
                var stepOnload = function (actions) {
                    $("#login").val("demo");
                    $("#password").val("demo");
                    actions.auto("form.oe_login_form button[type=submit]");
                };
                steps.splice(
                    position,
                    1,
                    {
                        title: "Go To Checkout",
                        extra_trigger: "#cart_products input.js_quantity[value=1]",
                        trigger: "a span:contains('Log in and checkout')"
                    },
                    {
                        title: "Log In",
                        trigger: "#login",
                        run: stepOnload
                    }
                );
            }
            break;
        }

    }
});
