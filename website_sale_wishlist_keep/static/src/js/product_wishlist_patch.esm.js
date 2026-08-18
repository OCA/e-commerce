/* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {ProductWishlist} from "@website_sale_wishlist/interactions/product_wishlist";
import {patch} from "@web/core/utils/patch";

patch(ProductWishlist.prototype, {
    /**
     * Keep the product in the wishlist after adding it to the cart, instead
     * of the standard behavior that removes it.
     *
     * @override
     */
    async addToCart(ev) {
        this.keepInWishlist = Boolean(this.el.querySelector("#b2b_wish")?.checked);
        try {
            await super.addToCart(ev);
        } finally {
            this.keepInWishlist = false;
        }
    },
    /**
     * Skip the removal triggered by `addToCart`, but keep it for the
     * explicit removal button.
     *
     * @override
     */
    async _removeProduct() {
        if (this.keepInWishlist) {
            return;
        }
        await super._removeProduct(...arguments);
    },
});
