/* License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
odoo.define("website_sale_vat_required.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "a:contains('Chair floor protection')",
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: "a[href='/shop/cart']",
            extra_trigger: "sup.my_cart_quantity:contains('1')",
        },
        {
            trigger: ".btn-primary:contains('Process Checkout')",
        },
        {
            content: "Next",
            trigger: ".btn-primary :contains('Next')",
        },
        {
            content: "Set VAT",
            trigger: "[name~='vat'].is-invalid",
            extra_trigger: "[name~='vat'].is-invalid",
            run: function () {
                $("input[name~='no_country_field'], [name~='vat'].is-invalid").val(
                    "US01234567891"
                );
                if ($(".div_name").hasClass("o_has_error")) {
                    $(".div_name input").val("Mr. Test");
                }
                if ($("#div_email").hasClass("o_has_error")) {
                    $("#div_email input").val("test@test.com");
                }
                if ($("#div_phone").hasClass("o_has_error")) {
                    $("#div_phone input").val("11111111");
                }
                if ($(".div_street").hasClass("o_has_error")) {
                    $(".div_street input").val("Test Street");
                }
                if ($(".div_city").hasClass("o_has_error")) {
                    $(".div_city input").val("Test City");
                }
                $(".div_zip input").val("12345");
                if ($(".div_country").hasClass("o_has_error")) {
                    $("#country_id option:eq(1)").attr("selected", true);
                }
                $('div.o_has_error input[name="accepted_legal_terms"]').prop(
                    "checked",
                    true
                );
            },
        },
        {
            content: "Next",
            trigger: ".btn-primary :contains('Next')",
        },
    ];
    tour.register(
        "website_sale_vat_required_tour",
        {
            url: "/shop",
            test: true,
        },
        steps
    );
    return {
        steps: steps,
    };
});
