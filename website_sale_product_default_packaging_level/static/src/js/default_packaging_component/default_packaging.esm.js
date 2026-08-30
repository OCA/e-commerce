import {Component, onWillDestroy, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class DefaultPackagingLevel extends Component {
    static template =
        "website_sale_product_default_packaging_level.DefaultPackagingLevel";
    static props = {
        default_product_packaging_level_name: {type: String, optional: true},
    };

    setup() {
        super.setup();
        this.state = useState({
            default_product_packaging_level_name:
                this.props.default_product_packaging_level_name,
        });
        const updateState = this._updateStateWithCombinationInfo.bind(this);
        this.env.bus.addEventListener("updateCombinationInfoDefaultPackaging", (res) =>
            updateState(res.detail)
        );
        onWillDestroy(() =>
            this.env.bus.removeEventListener(
                "updateCombinationInfoDefaultPackaging",
                updateState
            )
        );
    }

    /**
     * Update the state with the product combination info.
     *
     * @private
     * @param {Object} combinationInfo - The information on the current product variant.
     * @returns {void}
     */
    _updateStateWithCombinationInfo(combinationInfo) {
        this.state.default_product_packaging_level_name =
            combinationInfo.default_product_packaging_level_name;
    }
}

registry
    .category("public_components")
    .add(
        "website_sale_product_default_packaging_level.DefaultPackagingLevel",
        DefaultPackagingLevel
    );
