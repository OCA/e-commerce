odoo.define("website_sale_change_payment_fee.website_sale_fee", function(require) {
    "use strict";

    require("web.dom_ready");
    require("web.ajax");
    require("web.core");

    $(".o_payment_form").each(function() {
        var payment_form = this;
        var selected_acquirer = $("input[name='selected_acquirer_id']").val();

        $(payment_form).on("click", 'input[name="pm_id"]', function() {
            var clicked_acquirer = $(this)
                .prop("value")
                .substring(5);
            if (selected_acquirer !== clicked_acquirer) {
                $("#o_payment_form_pay").addClass("disabled");
                window.location.href =
                    "/shop/payment?payment_fee_id=" + clicked_acquirer;
            }
        });
    });
});
