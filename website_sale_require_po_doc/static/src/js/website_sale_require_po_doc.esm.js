// Copyright 2026 Isabel Andreu <isabel.andreu@forgeflow.com>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";

export class WebsiteSaleRequirePoDoc extends Interaction {
    static selector = "#div_customer_po_ref";

    dynamicContent = {
        "#customer_ref_input": {
            "t-on-input": this.onInput,
            "t-on-blur": this.onBlur,
        },
    };

    setup() {
        this.saveTimer = null;
        this.refInput = this.el.querySelector("#customer_ref_input");
        this.errorEl = this.el.querySelector("#customer_ref_error");

        const confirmForm = document.querySelector(
            'form[name="o_wsale_confirm_order"]'
        );
        if (confirmForm) {
            const onSubmit = (ev) => {
                if (!this.validate()) {
                    ev.preventDefault();
                    this.refInput.scrollIntoView({behavior: "smooth", block: "center"});
                }
            };
            confirmForm.addEventListener("submit", onSubmit);
            this.registerCleanup(() =>
                confirmForm.removeEventListener("submit", onSubmit)
            );
        }

        const onPayClick = (ev) => {
            const btn = ev.target.closest('[name="o_payment_submit_button"]');
            if (!btn) return;
            if (!this.validate()) {
                ev.stopImmediatePropagation();
                ev.preventDefault();
                this.refInput.scrollIntoView({behavior: "smooth", block: "center"});
            }
        };
        document.addEventListener("click", onPayClick, true);
        this.registerCleanup(() =>
            document.removeEventListener("click", onPayClick, true)
        );
    }

    validate() {
        const empty = !this.refInput.value.trim();
        this.refInput.classList.toggle("is-invalid", empty);
        if (this.errorEl) {
            this.errorEl.style.display = empty ? "block" : "none";
        }
        return !empty;
    }

    saveRef() {
        rpc("/shop/set_client_order_ref", {
            client_order_ref: this.refInput.value.trim(),
        });
    }

    onInput() {
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => this.saveRef(), 600);
    }

    onBlur() {
        clearTimeout(this.saveTimer);
        this.saveRef();
        this.validate();
    }
}

registry
    .category("public.interactions")
    .add("website_sale_require_po_doc.po_ref", WebsiteSaleRequirePoDoc);
