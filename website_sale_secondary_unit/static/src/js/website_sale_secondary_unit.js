odoo.define('website_sale_secondary_unit.animation', function (require) {
'use strict';

var core = require('web.core');
var sAnimation = require('website.content.snippets.animation');


sAnimation.registry.sale_secondary_unit = sAnimation.Class.extend({
    selector: ".secondary-unit",
    init: function (parent, editableMode) {
        this._super.apply(this, arguments);
        this.$secondary_uom = null;
        this.$secondary_uom_qty = null;
        this.$product_qty = null;
        this.secondary_uom_qty = null;
        this.secondary_uom_factor = null;
        this.product_uom_factor = null;
        this.product_qty = null;
    },
    start: function () {
        var self = this;
        self.$secondary_uom = $('#secondary_uom');
        self.$secondary_uom_qty = $('.secondary-quantity');
        self.$product_qty = $('.quantity');
        self._setValues();
        this.$target.on('change', '.secondary-quantity', function () {
            self._onChangeSecondaryUom();
        });
        this.$target.on('change', '#secondary_uom', function () {
            self._onChangeSecondaryUom();
        });
        this.$product_qty.on('change', null, function () {
            self._onChangeProductQty();
        });
        if(self.secondary_uom_qty){
            self._onChangeSecondaryUom();
        };
    },
    _setValues: function(){
        this.secondary_uom_qty = parseFloat(this.$target.find('.secondary-quantity').val());
        this.secondary_uom_factor = parseFloat($('option:selected', this.$secondary_uom).data('secondary-uom-factor'));
        this.product_uom_factor = parseFloat($('option:selected', this.$secondary_uom).data('product-uom-factor'));
        this.product_qty = parseFloat($('.quantity').val());
    },

    _onChangeSecondaryUom: function(){
        this._setValues()
        var factor = this.secondary_uom_factor * this.product_uom_factor;
        this.$product_qty.val(this.secondary_uom_qty * factor)
    },
    _onChangeProductQty: function(){
        this._setValues();
        var factor = this.secondary_uom_factor * this.product_uom_factor;
        this.$secondary_uom_qty.val(this.product_qty / factor);
    },
});

sAnimation.registry.sale_secondary_unit_cart = sAnimation.Class.extend({
    selector: ".oe_cart",
    init: function (parent, editableMode) {
        this._super.apply(this, arguments);
        this.$product_qty = null;
        this.secondary_uom_qty = null;
        this.secondary_uom_factor = null;
        this.product_uom_factor = null;
        this.product_qty = null;
    },
    start: function () {
        var self = this;
        this.$target.on('change', 'input.js_secondary_quantity[data-line-id]', function () {
            self._onChangeSecondaryUom(this);
        });
    },
    _setValues: function(order_line){
        this.$product_qty = this.$target.find('.quantity[data-line-id='+ order_line.dataset.lineId +']')
        this.secondary_uom_qty = parseFloat(order_line.value);
        this.secondary_uom_factor = parseFloat(order_line.dataset.secondaryUomFactor);
        this.product_uom_factor = parseFloat(order_line.dataset.productUomFactor);
    },
    _onChangeSecondaryUom: function(order_line){
        this._setValues(order_line);
        var factor = this.secondary_uom_factor * this.product_uom_factor;
        this.$product_qty.val(this.secondary_uom_qty * factor);
        this.$product_qty.trigger('change');
    },
});

});
