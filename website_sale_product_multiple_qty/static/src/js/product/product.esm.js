import {onWillUpdateProps} from "@odoo/owl";
import {Product} from "@sale/js/product/product";
import {patch} from "@web/core/utils/patch";

/**
 * Extend the Product component props so the configurator/product templates
 * can pass variant-level "sale multiple" information.
 *
 * This is used by QuantityButtons to enforce step logic.
 */
patch(Product, {
    props: {
        ...Product.props,
        is_multiple: {type: Number, optional: true},
        sale_multiple_qty: {type: Number, optional: true},
        product_uom_id: {type: Number, optional: true},
    },
});

patch(Product.prototype, {
    setup() {
        super.setup?.(...arguments);

        onWillUpdateProps((nextProps) => {
            const currentUomId = this.props.uom?.id;
            const nextUomId = nextProps.uom?.id;
            const uomChanged = currentUomId !== nextUomId;

            if (uomChanged) {
                /**
                 * Reset qty after UoM switch:
                 *
                 * - multiple product on default UoM
                 *   e.g. sale_multiple_qty = 10, selected UoM = Units
                 *   => reset qty to 10
                 *
                 * - multiple product on packaging UoM
                 *   e.g. sale_multiple_qty = 10, selected UoM = Box of 10
                 *   => reset qty to 1
                 *
                 * - product without sale multiple
                 *   => reset qty to 1
                 */
                const defaultQty = nextProps.is_multiple
                    ? nextUomId === nextProps.product_uom_id
                        ? parseFloat(nextProps.sale_multiple_qty || 1) || 1
                        : 1
                    : 1;
                this.env.setQuantity(nextProps.product_tmpl_id, defaultQty);
            }
        });
    },
});
