import {QuantityButtons} from "@sale/js/quantity_buttons/quantity_buttons";
import {patch} from "@web/core/utils/patch";

/**
 * Extend QuantityButtons props with "sale multiple" info
 */
patch(QuantityButtons, {
    props: {
        ...QuantityButtons.props,
        isMultiple: {type: [Boolean, Number], optional: true},
        saleMultipleQty: {type: Number, optional: true},
        productUomId: {type: Number, optional: true},
        currentUomId: {type: Number, optional: true},
        isMainProduct: {type: Boolean, optional: true},
    },
});

patch(QuantityButtons.prototype, {
    /**
     * Get the sales multiple values from component props.
     *
     * The step must follow the currently selected UoM:
     * - default product UoM => sale multiple qty
     * - packaging UoM => 1
     *
     */
    _getMultipleStep() {
        const isMultiple = Boolean(this.props.isMultiple);
        const saleMultipleQty = parseFloat(this.props.saleMultipleQty || 1) || 1;
        const productUomId = this.props.productUomId;
        const currentUomId = this.props.currentUomId;

        if (!isMultiple) {
            return {isMultiple: false, step: 1};
        }
        const step = currentUomId === productUomId ? saleMultipleQty : 1;
        return {isMultiple: true, step};
    },

    /**
     * Round up the quantity to the nearest step, with a minimum of 1 step.
     *
     * This matches "product page" behavior:
     * - no 0 here (configurator qty should not remove the product)
     * - always round UP when typing an arbitrary value
     */
    _roundUpToStep(qty, step) {
        const effectiveMin = Math.max(1, step);
        let v = parseFloat(qty || 0);

        if (!Number.isFinite(v) || v <= 0) {
            v = effectiveMin;
        }

        // Small epsilon used to compensate floating point precision errors
        const epsilon = step * 1e-9;
        v = Math.ceil(v / step - epsilon) * step;
        v = Math.max(v, effectiveMin);
        return v;
    },

    /**
     * "+" button behavior:
     * - non-multiple => standard flow
     * - multiple => +step
     *
     * @override
     */
    increaseQuantity() {
        const {isMultiple, step} = this._getMultipleStep();
        if (!isMultiple) {
            return super.increaseQuantity(...arguments);
        }
        const current = parseFloat(this.props.quantity || 0) || 0;
        const next = this._roundUpToStep(current + step, step);
        this.props.setQuantity(next);
    },

    /**
     * "-" button behavior:
     * - non-multiple => standard flow
     * - multiple => -step but never below effectiveMin (>= one step)
     *
     * @override
     */
    decreaseQuantity() {
        const {isMultiple, step} = this._getMultipleStep();
        if (!isMultiple) {
            return super.decreaseQuantity(...arguments);
        }
        const current = parseFloat(this.props.quantity || 0) || 0;
        const isMainProduct = Boolean(this.props.isMainProduct);

        // Main product: never go below one valid step.
        if (isMainProduct) {
            const effectiveMin = Math.max(1, step);
            const nextRaw = current - step;
            const next = nextRaw <= effectiveMin ? effectiveMin : nextRaw;
            this.props.setQuantity(next);
            return;
        }

        // Optional product: allow 0 so standard configurator can remove it.
        const next = Math.max(0, current - step);
        this.props.setQuantity(next);
    },

    /**
     * Manual input behavior (typing):
     * - non-multiple => standard flow
     * - multiple => round UP to step, then setQuantity
     *
     * @override
     */
    async setQuantity(event) {
        const {isMultiple, step} = this._getMultipleStep();
        if (!isMultiple) {
            return super.setQuantity(...arguments);
        }

        const inputQty = parseFloat(event.target.value);
        const rounded = this._roundUpToStep(inputQty, step);
        const didUpdateQuantity = await this.props.setQuantity(rounded);

        if (!didUpdateQuantity) {
            this.render();
        }
    },
});
