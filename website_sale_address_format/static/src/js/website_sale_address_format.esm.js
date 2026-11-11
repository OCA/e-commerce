/* global Option */
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.websiteSaleAddress =
    publicWidget.registry.websiteSaleAddress.extend({
        /**
         * Return the form input name for an address format field.
         *
         * @private
         * @param {String} fname
         */
        _getInputName(fname) {
            const inputNames = {
                state_code: "state_id",
                state_name: "state_id",
                country_code: "country_id",
                country_name: "country_id",
            };
            return inputNames[fname] || fname;
        },

        /**
         * @private
         */
        async _changeCountry(init = false) {
            const countryId = parseInt(this.addressForm.country_id.value);
            if (!countryId) {
                return;
            }

            const data = await rpc(`/shop/country_info/${parseInt(countryId)}`, {
                address_type: this.addressType,
            });

            if (data.phone_code !== 0) {
                this.addressForm.phone.placeholder = "+" + data.phone_code;
            } else {
                this.addressForm.phone.placeholder = "";
            }

            // Populate states and display
            var selectStates = this.addressForm.state_id;
            if (!init || selectStates.options.length === 1) {
                // Dont reload state at first loading (done in qweb)
                if (data.states.length || data.state_required) {
                    // Empty existing options, only keep the placeholder.
                    selectStates.options.length = 1;

                    // Create new options and append them to the select element
                    data.states.forEach((state) => {
                        const option = new Option(state[1], state[0]);
                        // Used by localizations
                        option.setAttribute("data-code", state[2]);
                        selectStates.appendChild(option);
                    });
                    this._showInput("state_id");
                } else {
                    // Empty existing options, only keep the placeholder.
                    selectStates.options.length = 1;
                    this._hideInput("state_id");
                }
            }

            // Manage fields order / visibility
            if (data.fields) {
                // [CUSTOM] Order and show fields as in the country's address format
                const inputNames = [
                    ...new Set(data.fields.map((fname) => this._getInputName(fname))),
                ].filter((name) => this.addressForm[name]);
                let prev = this._getInputDiv("street");
                for (const name of inputNames) {
                    const el = this._getInputDiv(name);
                    prev.after(el);
                    prev = el;
                }
                // A hidden required field would block the checkout.
                const isHidden = (name) =>
                    !inputNames.includes(name) && !data.required_fields.includes(name);
                ["street", "street2", "zip", "city"].forEach((name) => {
                    if (isHidden(name)) {
                        this._hideInput(name);
                    } else {
                        this._showInput(name);
                    }
                });
                // The state block above decides whether the country has states.
                if (data.online_address_format && isHidden("state_id")) {
                    this._hideInput("state_id");
                }
            }

            const required_fields = this.addressForm.querySelectorAll(":required");
            required_fields.forEach((element) => {
                // Remove requirement on previously required fields
                if (
                    !data.required_fields.includes(element.name) &&
                    !this.requiredFields.includes(element.name)
                ) {
                    this._markRequired(element.name, false);
                }
            });
            data.required_fields.forEach((fieldName) => {
                this._markRequired(fieldName, true);
            });
        },
    });
