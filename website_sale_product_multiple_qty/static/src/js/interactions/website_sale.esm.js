import {patch} from "@web/core/utils/patch";
import {WebsiteSale} from "@website_sale/interactions/website_sale";
import wSaleUtils from "@website_sale/js/website_sale_utils";

patch(WebsiteSale.prototype, {
    /**
     * Prevent "Enter" keypress in the quantity input
     * from submitting the form and reloading the page.
     * Keep rounding logic with manual input.
     *
     * @override
     */
    start() {
        const res = super.start?.(...arguments);

        this._onQtyKeydown = (ev) => {
            const input = ev.target;
            if (!input?.matches?.('input[name="add_qty"]')) return;
            if (ev.key !== "Enter") return;

            ev.preventDefault();
            ev.stopPropagation();

            // Force "change" including the multiple rounding
            input.dispatchEvent(new Event("change", {bubbles: true}));
        };

        this.el.addEventListener("keydown", this._onQtyKeydown, true);
        return res;
    },

    /**
     * Make sure to remove the event listener
     * when the widget is destroyed to prevent memory leaks.
     *
     * @override
     */
    destroy() {
        this.el?.removeEventListener?.("keydown", this._onQtyKeydown, true);
        this._onQtyKeydown = null;
        return super.destroy?.(...arguments);
    },

    /**
     * Resolve the root DOM node and return the add_qty input.
     */
    _getAddQtyInput(parent) {
        const root = parent?.el || parent?.[0] || parent || this.el;
        return root?.querySelector?.('input[name="add_qty"]');
    },

    /**
     * Read multiple step info from dataset.
     * Dataset is refreshed on each combination change.
     */
    _getMultipleInfoFromInput(input) {
        const isMultiple = input?.dataset?.isMultiple === "1";
        const step = parseFloat(input?.dataset?.uomStep || 1) || 1;

        // Keep track of the currently selected UoM to detect
        // packaging switches even when two packaging UoMs share the same step.
        const selectedUomId = String(input?.dataset?.selectedUomId || "");

        return {isMultiple, step, selectedUomId};
    },

    /**
     * Compute constraints for add_qty for both multiple/non-multiple cases.
     * For multiple products, effectiveMin must be >= step (we want one pack minimum).
     *
     * The quantity behavior depends on four business inputs coming from the backend:
     *
     * - sale_multiple_qty (product configuration)
     * - selected UoM ("Packaging" is chosen by the user on the website)
     * - product default UoM
     * - whether the selected UoM is considered a packaging
     *
     * These inputs are used to compute the step and the effective minimum quantity.
     * They are sent from the backend in the combination_info and stored in the dataset of the quantity input.
     *
     * Example scenarios
     * -----------------
     *
     * Product configuration:
     *
     *   Product default UoM = Units
     *   sale_multiple_uom_id = Box of 10
     *   → sale_multiple_qty = 10
     *
     *
     * CASE 1 — Default UoM (Units)
     *
     *   Selected UoM = Units
     *   Packaging? = NO
     *
     *   sale_multiple_qty = 10
     *   → step = 10
     *
     *   Quantity behavior:
     *     10 → 20 → 30 → ...
     *
     *   Dataset example:
     *     data-is-multiple="1"
     *     data-uom-step="10"
     *     data-min="10"
     *
     *
     * CASE 2 — Packaging UoM (Box of 10)
     *
     *   Selected UoM = Box of 10
     *   Packaging? = YES
     *
     *   sale_multiple_qty = 10
     *   → step = 1
     *
     *   Because we are counting packages, not units.
     *
     *   Quantity behavior:
     *     1 box → 2 boxes → 3 boxes
     *
     *   Dataset example:
     *     data-is-multiple="1"
     *     data-uom-step="1"
     *     data-min="1"
     *
     *
     * CASE 3 — Different variant with another multiple
     *
     *   Variant: Aluminium
     *   sale_multiple_uom_id = Box of 6
     *
     *   Selected UoM = Units
     *
     *   → step = 6
     *
     *   Quantity behavior:
     *     6 → 12 → 18 → ...
     *
     *
     * CASE 4 — Product without sale_multiple_uom_id
     *
     *   Selected UoM = Units
     *   → step = 1
     *
     *   Selected UoM = Packaging
     *   → step = 1
     *
     *   Standard Odoo quantity behavior.
     */
    _getAddQtyConstraints(input) {
        // Minimum quantity allowed by the input field.
        // Provided by backend via combination_info.
        //
        // Examples:
        //   multiple product (Units) → min = 10
        //   multiple product (Units) → min = 6
        //   packaging               → min = 1
        const min = parseFloat(input.dataset.min || 0);
        // Maximum allowed quantity.
        // Usually not set on product page → Infinity.
        const max = parseFloat(input.dataset.max || Infinity);
        const {isMultiple, step, selectedUomId} = this._getMultipleInfoFromInput(input);
        // Compute the effective minimum quantity.
        //
        // For multiple products we enforce at least one valid step.
        //
        // Examples:
        //
        //   step = 10
        //   min = 1
        //   → effectiveMin = 10
        //
        //   step = 6
        //   min = 6
        //   → effectiveMin = 6
        //
        //   packaging step = 1
        //   min = 1
        //   → effectiveMin = 1
        //
        // If backend sets a larger minimum we respect it.
        const effectiveMin = isMultiple ? Math.max(min, step) : min;

        return {min, max, isMultiple, step, effectiveMin, selectedUomId};
    },

    /**
     * Update the dataset attributes for the quantity input
     * based on the selected combination with sale multiple info.
     *
     */
    updateSaleMultiple(parent, combination) {
        const input = this._getAddQtyInput(parent);
        if (!input) return;

        input.dataset.saleMultipleQty = String(combination?.sale_multiple_qty ?? 1);
        input.dataset.isMultiple = combination?.is_multiple ? "1" : "0";

        // Use the step of the currently selected UoM:
        // - default UoM => sale multiple qty
        // - packaging UoM => 1
        input.dataset.uomStep = String(combination?.uom_qty_step ?? 1);

        // Store the selected UoM id to detect packaging-to-packaging switches.
        input.dataset.selectedUomId = String(combination?.selected_uom_id || "");

        // Keep the minimum aligned with the currently active step.
        input.dataset.min = String(combination?.uom_qty_step ?? 1);
    },

    /**
     * Detect if the selected UoM changed for the new combination.
     * Comparing only the step is not enough because two packaging UoMs
     * may both use step 1.
     */
    _didUomChange(input, combination) {
        const previousSelectedUomId = String(input?.dataset?.selectedUomId || "");
        const newSelectedUomId = String(combination?.selected_uom_id || "");
        return previousSelectedUomId !== newSelectedUomId;
    },

    /**
     * When the combination changes, update the dataset with sale multiple info.
     * Reset the quantity to the default value for the new variant
     * only if the variant has changed.
     *
     * @override
     */
    _onChangeCombination(ev, parent, combination) {
        const input = this._getAddQtyInput(parent);

        // Detect UoM switches before refreshing the dataset,
        // otherwise we would compare the new values with themselves.
        const uomChanged = input ? this._didUomChange(input, combination) : false;

        const res = super._onChangeCombination?.(...arguments);

        this.updateSaleMultiple(parent, combination);

        // Reset to default when switching variant or packaging/UoM.
        // This avoids keeping an invalid qty from the previous step context.
        if (combination?.variant_switched || uomChanged) {
            const updatedInput = this._getAddQtyInput(parent);
            if (!updatedInput) return res;

            const {isMultiple, step, effectiveMin} =
                this._getAddQtyConstraints(updatedInput);

            /**
             * Default qty per variant:
             * - multiple => at least one step (and still respect min if it is bigger)
             * - non-multiple => min
             */
            const defaultQty = isMultiple ? Math.max(step, effectiveMin) : effectiveMin;
            updatedInput.value = defaultQty;
        }

        return res;
    },

    /**
     * When the quantity is manually changed, apply rounding logic for multiples.
     *
     * @override
     */
    onChangeAddQuantity(ev) {
        const input = ev.currentTarget;

        // Non-multiple: keep standard logic.
        if (input.dataset.isMultiple !== "1") {
            return super.onChangeAddQuantity?.(...arguments);
        }

        const parent = wSaleUtils.getClosestProductForm(input);
        if (!parent) return;

        const {max, step, effectiveMin} = this._getAddQtyConstraints(input);

        let qty = parseFloat(input.value || 0);
        if (!Number.isFinite(qty) || qty <= 0) {
            qty = effectiveMin;
        }

        // Always round UP to the step.
        // Small epsilon used to compensate floating point precision errors
        const epsilon = step * 1e-9;
        qty = Math.ceil(qty / step - epsilon) * step;

        // Clamp to constraints (multiple effective min + max)
        qty = Math.min(Math.max(qty, effectiveMin), max);
        if (qty !== parseFloat(input.value || 0)) {
            input.value = qty;
        }

        // Keep standard behavior
        this.triggerVariantChange(parent);
    },

    /**
     * Apply a new qty to the input and trigger change.
     * This keeps one place where we dispatch the event.
     */
    _applyAddQtyAndTriggerChange(input, newQty) {
        const previousQty = parseFloat(input.value || 0);
        if (newQty === previousQty) return;

        input.value = newQty;
        input.dispatchEvent(new Event("change", {bubbles: true}));
    },

    /**
     * When the "+" or "-" buttons are clicked, update the quantity
     * according to the step and respecting the min/max constraints for multiples.
     *
     * @override
     */
    onChangeQuantity(ev) {
        const btn = ev?.currentTarget;
        const group = btn?.closest?.(".input-group");
        const input = group?.querySelector?.('input[name="add_qty"]');
        if (!input) return;

        // Non-multiple: keep standard behavior.
        if (input.dataset.isMultiple !== "1") {
            return super.onChangeQuantity?.(...arguments);
        }

        const {max, step, effectiveMin} = this._getAddQtyConstraints(input);

        const previousQty = parseFloat(input.value || 0);
        const delta = btn.name === "remove_one" ? -step : step;
        const quantity = previousQty + delta;

        /**
         * For multiple products:
         * - enforce effectiveMin (>= step)
         * - clamp to max
         * - we do not go below effectiveMin (product page does not support "0" remove)
         */
        const newQty = Math.min(Math.max(quantity, effectiveMin), max);

        this._applyAddQtyAndTriggerChange(input, newQty);
    },
});
