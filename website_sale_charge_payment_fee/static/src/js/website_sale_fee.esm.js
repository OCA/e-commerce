import {browser} from "@web/core/browser/browser";
import paymentForm from "@payment/js/payment_form";
paymentForm.include({
    async start() {
        await this._super(...arguments);
        const $paymentForm = this.target;
        const $selectedProvider = $paymentForm.querySelector(
            'input[name="o_payment_radio"][checked="True"]'
        );
        this.$selectedProvider = null;
        if ($selectedProvider) {
            this.$selectedProvider = $selectedProvider;
        }
    },

    async _selectPaymentOption(ev) {
        await this._super(...arguments);
        const $radio = ev.target;
        const providerId = this._getProviderId($radio);
        const paymentOptionId = this._getPaymentOptionId($radio);
        if (this.$selectedProvider !== $radio) {
            this.target
                .closest(".oe_website_sale")
                .querySelector('button[name="o_payment_submit_button"]').disabled =
                true;
            browser.location.href =
                "/shop/payment?provider_id=" +
                providerId +
                "&payment_option_id=" +
                paymentOptionId;
        }
    },
});
