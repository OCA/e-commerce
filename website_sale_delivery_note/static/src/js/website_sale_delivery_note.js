/* Copyright 2026 Domatix
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

/** Save the delivery note typed at the checkout on the current cart. */
(function () {
    "use strict";
    const input = document.getElementById("o_delivery_note");
    if (!input) {
        return;
    }
    input.addEventListener("change", () => {
        fetch("/shop/delivery_note", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                id: 1,
                params: {delivery_note: input.value},
            }),
        });
    });
})();
