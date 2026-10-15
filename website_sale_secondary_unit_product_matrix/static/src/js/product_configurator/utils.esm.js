/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

/**
 * @param {Object} product - A product of the configurator.
 * @returns {Object|undefined} The secondary unit it's sold in, if any.
 */
export function getSelectedSecondaryUom(product) {
    return product.secondary_uoms?.find(
        (secondaryUom) => secondaryUom.id === product.secondary_uom_id
    );
}
