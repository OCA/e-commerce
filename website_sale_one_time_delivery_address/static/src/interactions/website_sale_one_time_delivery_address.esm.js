// Copyright 2026 Camptocamp
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";

export class WebsiteSaleOneTimeDeliveryAddress extends Interaction {
    static selector = "#shop_checkout";

    dynamicContent = {
        "#o_one_time_delivery_checkbox": {"t-on-change": this.onOneTimeDeliveryToggle},
        ".card[data-address-type='delivery']": {
            "t-on-click": this.onDeliveryAddressSelected,
        },
    };

    /**
     * Reflect the one-time delivery mode in the checkout UI: show the info notice
     * and hide the "Same as delivery address" toggle (billing must stay on the
     * reseller). The toggle is only hidden, never removed, so other interactions
     * relying on its label text keep working.
     */
    _applyOneTimeDeliveryUi(active) {
        const notice = document.getElementById("o_one_time_delivery_notice");
        if (notice) {
            notice.classList.toggle("d-none", !active);
        }
        const billingToggle = document.getElementById(
            "use_delivery_as_billing_label"
        )?.parentElement;
        if (billingToggle) {
            billingToggle.classList.toggle("d-none", active);
        }
    }

    /**
     * Sync the one-time delivery checkbox state with the cart on the server and
     * update the contextual UI accordingly.
     */
    async onOneTimeDeliveryToggle(ev) {
        const checked = ev.currentTarget.checked;
        this._applyOneTimeDeliveryUi(checked);
        await rpc("/shop/update_one_time_delivery", {one_time_delivery: checked});
    }

    /**
     * Adapt the UI when the shopper selects a delivery address card: a
     * one_time_delivery contact enables one-time mode, any other address leaves
     * it. The cart flag itself is persisted server-side by the
     * /shop/update_address override triggered by the core checkout interaction.
     */
    onDeliveryAddressSelected(ev) {
        const isOneTime = ev.currentTarget.dataset.partnerType === "one_time_delivery";
        const checkbox = document.getElementById("o_one_time_delivery_checkbox");
        if (checkbox) {
            checkbox.checked = isOneTime;
        }
        this._applyOneTimeDeliveryUi(isOneTime);
    }
}

registry
    .category("public.interactions")
    .add(
        "website_sale_one_time_delivery_address.one_time_delivery",
        WebsiteSaleOneTimeDeliveryAddress
    );
