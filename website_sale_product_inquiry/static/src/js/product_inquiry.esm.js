/** @odoo-module */

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

class ProductInquiryInteraction extends Interaction {
    static selector = "#productInquiryModal";

    setup() {
        this._variantRefs = {};
        (this.el.dataset.variantRefs || "").split(",").forEach((entry) => {
            const sep = entry.indexOf(":");
            if (sep > 0) {
                this._variantRefs[entry.slice(0, sep)] = entry.slice(sep + 1);
            }
        });

        this._form = this.el.querySelector("#productInquiryForm");
        this._submitBtn = this.el.querySelector(".o_inquiry_submit");
        this._cancelBtn = this.el.querySelector(".o_inquiry_cancel");
        this._errorDiv = this.el.querySelector(".o_inquiry_error");
        this._successDiv = this.el.querySelector(".o_inquiry_success");
        this._footer = this.el.querySelector(".modal-footer");
        this._itemNoSpan = this.el.querySelector(".o_inquiry_item_no");
        this._productIdInput = this.el.querySelector(".o_inquiry_product_id");

        this.el.addEventListener("show.bs.modal", () => this._onShow());
        this.el.addEventListener("hidden.bs.modal", () => this._onHidden());
        this._form.addEventListener("submit", (ev) => this._onSubmit(ev));
        this._form.addEventListener("input", (ev) => this._onInput(ev));
    }

    _onInput(ev) {
        if (ev.target.validity.valid) {
            ev.target.classList.remove("is-invalid");
        }
    }

    _onShow() {
        const pageProductInput = document.querySelector(
            'form:not(#productInquiryForm) input[name="product_id"]'
        );
        if (!pageProductInput || !pageProductInput.value) return;
        const variantId = pageProductInput.value;
        if (this._productIdInput) {
            this._productIdInput.value = variantId;
        }
        if (this._itemNoSpan) {
            const ref = this._variantRefs[variantId];
            if (ref !== undefined) {
                this._itemNoSpan.textContent = ref;
            }
        }
    }

    _setButtons(disabled) {
        this._submitBtn.disabled = disabled;
        this._cancelBtn.disabled = disabled;
    }

    _showError(message) {
        this._errorDiv.textContent = message;
        this._errorDiv.classList.remove("d-none");
        this._setButtons(false);
    }

    async _onSubmit(ev) {
        ev.preventDefault();
        if (!this._form.checkValidity()) {
            this._form.querySelectorAll(":invalid").forEach((el) => {
                el.classList.add("is-invalid");
            });
            return;
        }
        this._setButtons(true);
        this._errorDiv.classList.add("d-none");

        try {
            const response = await fetch("/shop/product/inquiry", {
                method: "POST",
                body: new FormData(this._form),
            });
            const data = await response.json();
            if (data.success) {
                this._form.classList.add("d-none");
                this._successDiv.classList.remove("d-none");
                this._footer.classList.add("d-none");
            } else {
                this._showError(data.error || "An error occurred. Please try again.");
            }
        } catch {
            this._showError("An error occurred. Please try again.");
        }
    }

    _onHidden() {
        this._form.reset();
        this._form
            .querySelectorAll(".is-invalid")
            .forEach((el) => el.classList.remove("is-invalid"));
        this._form.classList.remove("d-none");
        this._errorDiv.classList.add("d-none");
        this._errorDiv.textContent = "";
        this._successDiv.classList.add("d-none");
        this._footer.classList.remove("d-none");
        this._setButtons(false);
    }
}

registry
    .category("public.interactions")
    .add("website_sale_product_inquiry.inquiry", ProductInquiryInteraction);
