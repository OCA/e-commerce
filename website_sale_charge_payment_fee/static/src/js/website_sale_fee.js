/** @odoo-module **/
import PaymentForm from "@payment/js/payment_form";
import {jsonrpc} from "@web/core/network/rpc_service";

PaymentForm.include({
    async _expandInlineForm(radio) {
        await this._super(...arguments);
        const isFee = this._getIsFeeFromRadio(radio);
        if (isFee === "True") {
            const paymentOptionId = parseInt(radio.dataset.providerId, 10);
            jsonrpc("/shop/payment/get_fee", {
                provider_id: paymentOptionId,
            }).then((result) => {
                var amountDelivery = document.querySelector(
                    "#order_delivery .monetary_field"
                );
                var amount_payment_fee = document.querySelector(
                    "#order_payment_fee .monetary_field"
                );
                var amountUntaxed = document.querySelector(
                    "#order_total_untaxed .monetary_field"
                );
                var amountTax = document.querySelector(
                    "#order_total_taxes .monetary_field"
                );
                var amountTotal = document.querySelectorAll(
                    "#order_total .monetary_field, #amount_total_summary.monetary_field"
                );

                if (amountDelivery) {
                    amountDelivery.innerHTML = result.new_amount_delivery;
                }

                amountUntaxed.innerHTML = result.new_amount_untaxed;
                amountTax.innerHTML = result.new_amount_tax;
                amount_payment_fee.innerHTML = result.new_amount_payment_fee;
                amountTotal.forEach(
                    (total) => (total.innerHTML = result.new_amount_total)
                );
                this._updateAmountPaymentFee(result.new_amount_total_raw);
            });
            $("tr#order_payment_fee").removeClass("d-none");
        } else {
            $("tr#order_payment_fee").addClass("d-none");
        }
    },

    _getIsFeeFromRadio: (radio) => $(radio).data("is-fee"),

    /**
     * Update the total amount to be paid.
     *
     * Called upon change of shipping method
     *
     * @private
     * @param {float} amount
     */
    _updateAmountPaymentFee: function (amount) {
        this.paymentContext.amount = amount;
    },

    /**
     * @override
     */
    _selectPaymentOption: function (ev) {
        this._super(...arguments);

        const checkedRadio = $(ev.currentTarget)[0];
        const paymentOptionId = parseInt(checkedRadio.dataset.providerId, 10);
        const isFee = this._getIsFeeFromRadio(checkedRadio);
        if (isFee === "True") {
            jsonrpc("/shop/payment/get_fee", {
                provider_id: paymentOptionId,
            }).then((result) => {
                var amountDelivery = document.querySelector(
                    "#order_delivery .monetary_field"
                );
                var amount_payment_fee = document.querySelector(
                    "#order_payment_fee .monetary_field"
                );
                var amountUntaxed = document.querySelector(
                    "#order_total_untaxed .monetary_field"
                );
                var amountTax = document.querySelector(
                    "#order_total_taxes .monetary_field"
                );
                var amountTotal = document.querySelectorAll(
                    "#order_total .monetary_field, #amount_total_summary.monetary_field"
                );

                if (amountDelivery) {
                    amountDelivery.innerHTML = result.new_amount_delivery;
                }
                amountUntaxed.innerHTML = result.new_amount_untaxed;
                amountTax.innerHTML = result.new_amount_tax;
                amount_payment_fee.innerHTML = result.new_amount_payment_fee;
                amountTotal.forEach(
                    (total) => (total.innerHTML = result.new_amount_total)
                );
                this._updateAmountPaymentFee(result.new_amount_total_raw);
            });
            $("tr#order_payment_fee").removeClass("d-none");
        } else {
            $("tr#order_payment_fee").addClass("d-none");
        }
    },
});
