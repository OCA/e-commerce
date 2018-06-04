$(document).ready(function () {

    if (_.str.startsWith(window.location.pathname, "/shop/payment")) {
        var $pay_button = $('.oe_sale_acquirer_button button');
        $pay_button.prop('disabled', false);

        // When choosing a payment, update the quotation. Disable the 'Pay
        // Now' button to avoid being redirected to payment acquirer if the delivery carrier update is
        // not over.
        var $payment_method = $("#payment_method");
        var $selected_acquirer_id = $("input[name='selected_acquirer_id']");
        var selected_acquirer_id = $selected_acquirer_id.val();
        $payment_method.find("input[name='acquirer']").click(function (ev) {
            var payment_id = $(ev.currentTarget).val();
            // We need to check selected_acquirer_id because website_sale module clicks on checked acquirer at page load.
            // See website_sale/static/src/js/website_sale_payment.js :
            // .find("input[name='acquirer']:checked").click();
            // Without this check, redirect would be performed right after page load
            if (selected_acquirer_id != null && payment_id != selected_acquirer_id) {
                $pay_button.prop('disabled', true);
                window.location.href = '/shop/payment?payment_fee_id=' + payment_id;
            }
        });
    }

});
