odoo.define("website_sale_charge_payment_fee.website_sale_fee", (require) => {
    "use strict";

    const checkoutForm = require("payment.checkout_form");
    const manageForm = require("payment.manage_form");

    const PaymentMixin = {
        _getIsFeeFromRadio: (radio) => $(radio).data("is-fee"),
        /**
         * @override
         */
        _onClickPaymentOption: function (ev) {
            this._super.apply(this, arguments);

            const checkedRadio = $(ev.currentTarget).find(
                'input[name="o_payment_radio"]'
            )[0];
            $(checkedRadio).prop("checked", true);
            const $amount_payment_fee = $("#order_payment_fee .monetary_field");
            const paymentOptionId = this._getPaymentOptionIdFromRadio(checkedRadio);
            const isFee = this._getIsFeeFromRadio(checkedRadio);
            if (isFee === "True") {
                $("tr#order_payment_fee").removeClass("d-none");
            } else {
                $("tr#order_payment_fee").addClass("d-none");
            }
            this._rpc({
                route: "/shop/payment/get_fee",
                params: {
                    provider_id: paymentOptionId,
                },
            }).then((result) => {
                $amount_payment_fee.html(result.amount_payment_fee);
            });
        },
    };

    checkoutForm.include(PaymentMixin);
    manageForm.include(PaymentMixin);
});
