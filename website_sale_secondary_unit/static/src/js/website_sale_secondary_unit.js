odoo.define("website_sale_secondary_unit.animation", function (require) {
    "use strict";

    const VariantMixin = require("sale.VariantMixin");
    const sAnimation = require("website.content.snippets.animation");

    sAnimation.registry.sale_secondary_unit = sAnimation.Class.extend(VariantMixin, {
        selector: ".secondary-unit",
        // eslint-disable-next-line no-unused-vars
        init: function (parent, editableMode) {
            this._super.apply(this, arguments);
            this.$secondary_uom = null;
            this.$product_qty = null;
            this.secondary_uom_factor = null;
            this.product_uom_factor = null;
            this.product_qty = null;
        },
        start: function () {
            const _this = this;
            this.$secondary_uom = $("#secondary_uom");
            this.$product_qty = $(".quantity");
            this._setValues();
            this.$target.on(
                "change",
                "#secondary_uom",
                this._onChangeSecondaryUom.bind(this)
            );
            this.$product_qty.on("change", null, this._onChangeProductQty.bind(this));
            return this._super.apply(this, arguments).then(function () {
                _this._onChangeSecondaryUom();
            });
        },
        _setValues: function () {
            this.secondary_uom_factor = Number(
                $("option:selected", this.$secondary_uom).data("secondary-uom-factor")
            );
            this.product_uom_factor = Number(
                $("option:selected", this.$secondary_uom).data("product-uom-factor")
            );
            this.product_qty = Number($(".quantity").val());
            this.uom_factor = this.secondary_uom_factor * this.product_uom_factor
        },

        _onChangeSecondaryUom: function (ev) {
            if (!ev) {
                // HACK: Create a fake event to locate the form on "onChangeAddQuantity"
                // odoo method
                ev = jQuery.Event("fakeEvent");
                ev.currentTarget = $(".form-control.quantity");
            }
            this._setValues();
            this.$product_qty.val(this.uom_factor);
            this.onChangeAddQuantity(ev);
        },
        _onChangeProductQty: function () {
            // This method is called when the product quantity is changed
            // It will adjust the quantity to be a multiple of the uom factor
            // Constraint: Quantity cannot be less than 0
            this._setValues();
            const product_qty = this.$product_qty.val();
            var qty_ratio = parseFloat(product_qty / this.uom_factor);
            if (qty_ratio < 1) {
                qty_ratio = 1;
            }
            // By using round, we get the closest ratio telling us if the value
            // is decreased (1.75 -> 2) or increased (2.25 -> 2)
            var nearest_ratio = Math.round(qty_ratio);
            if (nearest_ratio !== qty_ratio) {
                if (nearest_ratio < qty_ratio) {  // increased
                    qty_ratio = Math.ceil(qty_ratio);
                } else {  // decreased
                    qty_ratio = Math.floor(qty_ratio);
                }
            }
            this.$product_qty.val(qty_ratio * this.uom_factor);
        },
    });

    sAnimation.registry.sale_secondary_unit_cart = sAnimation.Class.extend({
        selector: ".oe_cart",
        // eslint-disable-next-line no-unused-vars
        init: function (parent, editableMode) {
            this._super.apply(this, arguments);
            this.$product_qty = null;
            this.secondary_uom_qty = null;
            this.secondary_uom_factor = null;
            this.product_uom_factor = null;
            this.product_qty = null;
        },
        start: function () {
            var _this = this;
            this.$target.on(
                "change",
                "input.js_secondary_quantity[data-line-id]",
                function () {
                    _this._onChangeSecondaryUom(this);
                }
            );
        },
        _setValues: function (order_line) {
            this.$product_qty = this.$target.find(
                ".quantity[data-line-id=" + order_line.dataset.lineId + "]"
            );
            this.secondary_uom_qty = Number(order_line.value);
            this.secondary_uom_factor = Number(order_line.dataset.secondaryUomFactor);
            this.product_uom_factor = Number(order_line.dataset.productUomFactor);
        },
        _onChangeSecondaryUom: function (order_line) {
            this._setValues(order_line);
            const factor = this.secondary_uom_factor * this.product_uom_factor;
            this.$product_qty.val(this.secondary_uom_qty * factor);
            this.$product_qty.trigger("change");
        },
    });
});

odoo.define("website_sale_secondary_unit.website_sale", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    require("website_sale.website_sale");

    publicWidget.registry.WebsiteSale.include({
        _submitForm: function () {
            if (
                !("secondary_uom_id" in this.rootProduct) &&
                $(this.$target).find("#secondary_uom").length
            ) {
                this.rootProduct.secondary_uom_id = $(this.$target)
                    .find("#secondary_uom")
                    .val();
            }

            this._super.apply(this, arguments);
        },
    });
});
