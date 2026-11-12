/* Copyright 2020 Sergio Teruel
   Copyright 2026 Tecnativa - Adasat Torres
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";
import {browser} from "@web/core/browser/browser";
import {rpc} from "@web/core/network/rpc";

export class WebsiteSaleTaxToggle extends Interaction {
    static selector = ".js_tax_toggle_management";

    dynamicContent = {
        input: {
            "t-on-change": this.onTaxToggleChange,
        },
    };

    async onTaxToggleChange() {
        await rpc(this.el.dataset.controller, {});
        browser.location.reload();
    }
}

registry
    .category("public.interactions")
    .add("website_sale_tax_toggle.tax_toggle", WebsiteSaleTaxToggle);
