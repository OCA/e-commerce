odoo.define("website_sale_charge_payment_fee.website_sale_fee", (require) => {
    "use strict";

    const checkoutForm = require("payment.checkout_form");
    const manageForm = require("payment.manage_form");

    const PaymentMixin = {
        /**
         * @override
         */
        _displayInlineForm: function (radio) {
            this._super.apply(this, arguments);
            const $amount_payment_fee = $("#order_payment_fee .monetary_field");
            const paymentOptionId = this._getPaymentOptionIdFromRadio(radio);
            this._rpc({
                route: "/shop/payment/update_fee",
                params: {
                    payment_fee_id: paymentOptionId,
                },
            }).then((result) => {
                $amount_payment_fee.html(result.amount_payment_fee);
            });
        },
    };

    checkoutForm.include(PaymentMixin);
    manageForm.include(PaymentMixin);
});
