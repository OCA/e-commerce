import {PaymentForm} from "@payment/interactions/payment_form";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";

patch(PaymentForm.prototype, {
    setup() {
        super.setup(...arguments);
        this.selectedProvider = this.el.querySelector(
            'input[name="o_payment_radio"]:checked'
        );
    },

    async selectPaymentOption(ev) {
        await super.selectPaymentOption(...arguments);
        const radio = ev.target;
        const providerId = this._getProviderId(radio);
        const paymentOptionId = this._getPaymentOptionId(radio);
        if (this.selectedProvider !== radio) {
            this._disableButton();
            browser.location.href =
                "/shop/payment?provider_id=" +
                providerId +
                "&payment_option_id=" +
                paymentOptionId;
        }
    },
});
