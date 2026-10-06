/* global Option */
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.websiteSaleAddress =
    publicWidget.registry.websiteSaleAddress.extend({
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
                    this._hideInput("state_id");
                }
            }

            // Manage fields order / visibility
            if (data.fields) {
                // [CUSTOM][DEL] Following 5 lines
                // if (data.zip_before_city) {
                //     this._getInputDiv('zip').after(this._getInputDiv('city'));
                // } else {
                //     this._getInputDiv('zip').before(this._getInputDiv('city'));
                // }
                // [CUSTOM][ADD] Following 11 lines: sort fields according to
                // online_address_format of the country
                let prev = this._getInputDiv("street");
                for (const fname of data.fields) {
                    let key = fname.split("_")[0];
                    if (key === "state") key = "state_id";
                    if (key === "country") key = "country_id";
                    const el = this._getInputDiv(key);
                    if (el) {
                        prev.after(el);
                        prev = el;
                    }
                }
                // [CUSTOM][DEL] Following line
                // var all_fields = ['street', 'zip', 'city'];
                // [CUSTOM][ADD] street2 and state_code
                var all_fields = [
                    "street",
                    "street2",
                    "zip",
                    "city",
                    "state_code",
                    "state_name",
                ];
                // [EDIT] Following 13 lines
                const toInputName = (fname) => {
                    const key = fname.split("_")[0];
                    if (key === "state") return "state_id";
                    return key;
                };
                all_fields.forEach((fname) => {
                    const input = toInputName(fname);
                    if (data.fields.includes(fname)) {
                        this._showInput(input);
                    } else {
                        this._hideInput(input);
                    }
                });
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
