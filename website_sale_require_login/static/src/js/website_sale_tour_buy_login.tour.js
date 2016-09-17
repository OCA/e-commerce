/* © 2015 Antiun Ingeniería S.L. - Jairo Llopis
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('website_sale_require_login.tour', function(require) {
    
    "use strict";
    
    var $ = require('$');
    var Tour = require('web.Tour');
    
    var steps = Tour.tours.shop_buy_product.steps;

    // Gets user name from login menu (see openerp.Tour.log)
    function user() {
        return $(".navbar .dropdown:has(>.js_usermenu) a:first, " +
                 ".navbar .oe_topbar_name, " +
                 ".pos .username").text();
    }

    // Alter expected buying workflow for public users
    if (!user()) {
        var stepOnload = function () {
            $("#login").val("demo");
            $("#password").val("demo");
        };
        for (var position = 0; position < steps.length; position++) {
            if (steps[position].title === "go to checkout") {
                steps.splice(
                    position,
                    1,
                    {
                        title: "Go To Checkout",
                        waitFor: "#cart_products input.js_quantity[value=1]",
                        element: "a span:contains('Log in and checkout')",
                    },
                    {
                        title: "Log In",
                        element: "form.oe_login_form button[type=submit]",
                        onload: stepOnload,
                    }
                );
                break;
            }
        }
    }
    
});
