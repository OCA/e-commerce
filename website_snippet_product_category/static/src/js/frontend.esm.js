// Copyright 2020 Tecnativa - Alexandre Díaz
// Copyright 2025 Tecnativa - Pilar Vargas
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import {Interaction} from "@web/public/interaction";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";

export class ProductCategory extends Interaction {
    static selector = ".js_product_category";

    setup() {
        // Prevent user edition
        this.el.setAttribute("contenteditable", "false");
    }

    /**
     * Asynchronous server side template rendering
     */
    async willStart() {
        const template =
            this.el.dataset.template ||
            "website_snippet_product_category.s_product_category_items";
        try {
            this.html = await this.waitFor(
                rpc("/website_sale/render_product_category", {template})
            );
        } catch {
            this.html = null;
        }
    }

    start() {
        if (this.html === null) {
            if (this.services["public.interactions"]?.editMode) {
                this.renderError();
            }
            return;
        }
        const scratchEl = document.createElement("div");
        scratchEl.innerHTML = this.html;
        const count = scratchEl.querySelector("input[name='object_count']")?.value;
        if (!count) {
            this.renderWarning();
            return;
        }
        this.el.innerHTML = this.html;
    }

    renderWarning() {
        const warningEl = document.createElement("div");
        warningEl.className = "alert alert-warning alert-dismissible text-center";
        warningEl.textContent = _t(
            "No categories were found. Make sure you have categories defined."
        );
        this.el.append(warningEl);
    }

    renderError() {
        const errorEl = document.createElement("p");
        errorEl.className = "text-danger";
        errorEl.textContent = _t(
            "An error occurred with this product categories block. If the problem persists, please consider deleting it and adding a new one"
        );
        this.el.append(errorEl);
    }
}

registry
    .category("public.interactions")
    .add("website_snippet_product_category.product_category", ProductCategory);
registry
    .category("public.interactions.edit")
    .add("website_snippet_product_category.product_category", {
        Interaction: ProductCategory,
    });
