import {parseDate, parseDateTime} from "@web/core/l10n/dates";
import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

const WebsiteSaleCheckout = publicWidget.registry.WebsiteSaleCheckout;

WebsiteSaleCheckout.include({
    disabledInEditableMode: true,

    async start() {
        this.minDate = luxon.DateTime.now();
        await this._super(...arguments);
        this.deliveryDateElement = this.el.querySelector("#delivery_date_element");
        this.pickerElement = this.el.querySelector(
            "[data-widget='delivery-date-picker']"
        );
        const value = this.pickerElement.defaultValue;
        this.pickerError = this.el.querySelector("#datetimePickerError");
        this.picker = await this.call("datetime_picker", "create", {
            target: this.pickerElement,
            onApply: this._onChangeDatePicker.bind(this),
            format: "yyyy-MM-dd HH:mm",
            pickerProps: {
                type: "datetime",
                minDate: this.minDate,
                rounding: 30,
                value: parseDateTime(value),
            },
        });
        await this.picker.enable();
    },

    async _onChangeDatePicker(newDate) {
        const carrierEl = this.el.querySelector(
            'input[name="o_delivery_radio"]:checked'
        );
        const carrierId = parseInt(carrierEl.dataset.dmId, 10);
        if (!carrierId || !newDate) return;
        const result = await rpc("/shop/set_delivery_date", {
            carrier_id: carrierId,
            delivery_date: newDate.setZone("utc").toFormat("yyyy-MM-dd HH:mm"),
        });
        let error = "";
        if (result.valid) {
            this.pickerElement.classList.remove("is-invalid");
            this.pickerElement.classList.add("is-valid");
        } else {
            this.pickerElement.value = "";
            this.pickerElement.classList.add("is-invalid");
            this.pickerElement.classList.remove("is-valid");
            error = result.message;
        }
        this.pickerError.innerText = error;
    },

    async _updateDeliveryMethod(radio) {
        await this._super(...arguments);
        await this._updateDeliveryDate(radio.dataset.dmId);
    },

    async _updateDeliveryDate(dmId) {
        const carrierId = parseInt(dmId, 10);
        if (!carrierId) return;
        const result = await rpc("/shop/delivery_date_constraints", {
            carrier_id: carrierId,
        });
        if (result.min_date) {
            this.minDate = parseDate(result.min_date);
        }
        if (!Object.prototype.hasOwnProperty.call(this, "pickerElement")) return;
        this.pickerElement.value = "";
        this.pickerElement.classList.remove("is-invalid", "is-valid");
        this.pickerError.innerText = "";
        this.deliveryDateElement.classList.toggle("d-none", !result.visible);
        if (result.min_date) {
            this.picker.state.minDate = this.minDate;
        }
        if (result.max_date) {
            this.picker.state.maxDate = parseDate(result.max_date);
        }
    },

    destroy() {
        this.picker();
        return this._super(...arguments);
    },
});
