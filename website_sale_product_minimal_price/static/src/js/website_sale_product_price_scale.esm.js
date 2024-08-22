/** @odoo-module **/

import {formatMonetary} from "@web/views/fields/formatters";
import {jsonrpc} from "@web/core/network/rpc_service";
import {renderToFragment} from "@web/core/utils/render";
import VariantMixin from "@website_sale/js/sale_variant_mixin";
import publicWidget from "@web/legacy/js/public/public_widget";

VariantMixin._onChangeQtyWebsiteSale = async function (ev, $parent, combination) {
    const $node = document.getElementById("js_product_price_scale");
    if (!this.isWebsite || !$node) {
        return;
    }
    const data = await jsonrpc(
        "/website_sale/get_combination_info_pricelist_atributes",
        {
            product_id: combination.product_id,
        }
    );
    const $price_scale = renderToFragment(
        "website_sale_product_minimal_price.pricelist_block",
        {
            ...data,
            ...this._additionalProductScaleContext(),
        }
    );
    $node.innerHTML = "";
    $node.appendChild($price_scale);
};

publicWidget.registry.WebsiteSale.include({
    /**
     * Add _onChangeQtyWebsiteSale to _onChangeCombination method.
     *
     * @override
     */
    _onChangeCombination: function () {
        this._super.apply(this, arguments);
        VariantMixin._onChangeQtyWebsiteSale.apply(this, arguments);
    },
    _additionalProductScaleContext: function () {
        return {formatMonetary};
    },
});
