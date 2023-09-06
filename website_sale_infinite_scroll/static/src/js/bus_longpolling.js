odoo.define("website_sale_infinite_scroll.Longpolling", function (require) {
    "use strict";

    var LongpollingBus = require("bus.Longpolling");

    // Enable fast backward/forward from bfcache
    LongpollingBus.include({
        init: function () {
            this._super.apply(this, arguments);
            $(window).unbind("unload");
            $(window).on(
                "pagehige." + this._longPollingBusId,
                this._onFocusChange.bind(this, {focus: false})
            );
        },
        destroy: function () {
            this._super.apply(this, arguments);
            $(window).off("pagehige." + this.bus_id);
        },
    });
});
