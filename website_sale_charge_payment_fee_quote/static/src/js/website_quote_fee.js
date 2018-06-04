$(document).ready(function () {

    if (_.str.startsWith(window.location.pathname, "/quote/")) {
        var $pay_button = $('.oe_quote_acquirer_button button');
        $pay_button.prop('disabled', false);
        var $payment_method = $("#payment_method");
        var $selected_acquirer_id = $("input[name='selected_acquirer_id']");
        var selected_acquirer_id = $selected_acquirer_id.val();
        var selected_acquirer_charge_fee = $selected_acquirer_id.data('charge-fee');

        $payment_method.find("input[name='acquirer']").click(function (ev) {
            var payment_id = $(ev.currentTarget).val();
            var payment_id_charge_fee = $(ev.currentTarget).data('charge-fee');
            // See website_sale_charge_payment_fee js
            if (selected_acquirer_id != null && payment_id != selected_acquirer_id) {
                // if at least one has fee, we need to recompute.
                // The only case when we don't recompute is when both acquirers have not fee
                if (selected_acquirer_charge_fee == "True" || payment_id_charge_fee == "True") {
                    $pay_button.prop('disabled', true);
                    window.location.href = window.location.origin +
                        window.location.pathname + '?payment_fee_id=' + payment_id;
                }
            }
        });
    }

});
