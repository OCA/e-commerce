odoo.define("website_sale_change_payment_fee.website_sale_fee", function(require) {
    "use strict";

    require("web.dom_ready");
    require("web.ajax");
    require("web.core");

    $(".o_payment_form").each(function() {
        var selected_acquirer = $("input[name='selected_acquirer_id']").val();

        $(this).on("click", 'input[name="pm_id"]', function() {
            var clicked_acquirer = $(this)
                .prop("value")
                .substring(5);  // Represents the form id.
            if (selected_acquirer !== clicked_acquirer) {
                // Follow standard logic disabling the "Pay Now" button
                // https://github.com/odoo/odoo/blob/c2cce50f75096fcc9f940d16bb0ecf40a2899d60/addons/website_sale_delivery/static/src/js/website_sale_delivery.js#L56
                $("#o_payment_form_pay").prop('disabled', true);
                window.location.href =
                    "/shop/payment?payment_fee_id=" + clicked_acquirer;
            }
        });
    });
});
