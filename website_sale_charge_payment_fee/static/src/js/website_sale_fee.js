/** @odoo-module **/
import PaymentForm from "@payment/js/payment_form";
import {jsonrpc} from "@web/core/network/rpc_service";
import wSaleUtils from "@website_sale/js/website_sale_utils";

PaymentForm.include({
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
        const $amount_payment_fee = $("#order_payment_fee .monetary_field");
        const paymentOptionId = parseInt(checkedRadio.dataset.providerId, 10);
        const isFee = this._getIsFeeFromRadio(checkedRadio);
        if (isFee === "True") {
            $("tr#order_payment_fee").removeClass("d-none");
        } else {
            $("tr#order_payment_fee").addClass("d-none");
        }
        jsonrpc("/shop/payment/get_fee", {
            provider_id: paymentOptionId,
        }).then((result) => {
            jsonrpc("/shop/cart/update_json", {
                line_id: result.line_id,
                product_id: result.product_id,
                set_qty: 1,
                display: true,
            }).then((data) => {
                wSaleUtils.updateCartNavBar(data);

                if (data.amount !== undefined) {
                    document
                        .querySelectorAll(
                            "#amount_total_summary.monetary_field .oe_currency_value"
                        )
                        .forEach((el) => {
                            el.textContent = data.amount;
                        });
                }
                // Propagating the change to the express checkout forms
                this._updateAmountPaymentFee(data.amount);
                setTimeout(() => {
                    $("tr#order_payment_fee").removeClass("d-none");
                    $amount_payment_fee.html(result.amount_payment_fee);
                }, 50);
            });
        });
    },
});
