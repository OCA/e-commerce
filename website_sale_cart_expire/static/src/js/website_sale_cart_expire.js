odoo.define("website_sale_cart_expire", (require) => {
    "use strict";

    const publicWidget = require("web.public.widget");
    const time = require("web.time");

    /**
     * Cart Expire Timer widget.
     *
     * Displays a countdown timer for the cart expiration date.
     */
    publicWidget.registry.WebsiteSaleCartExpireTimer = publicWidget.Widget.extend({
        selector: ".my_cart_expiration",

        /**
         * @override
         */
        start: async function () {
            await this._super.apply(this, arguments);
            this._setExpirationDate(this.$el.data("order-expire-date"));
            const remainingMs = this._getRemainingMs();
            if (remainingMs > 0) {
                this._renderTimer(remainingMs);
                this._startTimer();
            }
            // Attempts to hook into the cart quantity widget to update the expiration date
            // whenever it changes.
            this.$el.siblings(".my_cart_quantity").on(
                "DOMSubtreeModified",
                _.debounce(() => this._refreshExpirationDate(), 250)
            );
        },
        /**
         * @override
         */
        destroy: function () {
            this.$el.remove();
            this._stopTimer();
            return this._super.apply(this, arguments);
        },
        /**
         * Sets the timer target date.
         *
         * @param {String|Date} expireDate
         */
        _setExpirationDate: function (expireDate) {
            if (typeof expireDate === "string") {
                expireDate = time.str_to_datetime(expireDate);
            }
            this.expireDate = expireDate ? moment(expireDate) : false;
        },
        /**
         * @returns {Number}
         */
        _getRemainingMs: function () {
            return this.expireDate ? this.expireDate.diff(moment()) : 0;
        },
        /**
         * Starts the timer.
         */
        _startTimer: function () {
            this._stopTimer();
            this.timer = setInterval(this._refreshTimer.bind(this), 1000);
        },
        /**
         * Stops the timer.
         */
        _stopTimer: function () {
            if (this.timer) {
                clearInterval(this.timer);
            }
        },
        /**
         * Refreshes the countdown timer.
         * It destroys itself if the countdown reaches 0.
         */
        _refreshTimer: function () {
            const remainingMs = this._getRemainingMs();
            this._renderTimer(remainingMs);
            if (remainingMs <= 0) {
                this._stopTimer();
                this._refreshExpirationDate();
            }
        },
        /**
         * Updates the remaining time on the dom
         */
        _renderTimer: function (remainingMs) {
            const remainingMsRounded = Math.ceil(remainingMs / 1000) * 1000;
            // Don't show the timer if remaining time is less than 1 hour
            if (remainingMsRounded >= 3600000) {
                return this.$el.hide();
            }
            this.$el.show();
            // Format the countdown timer
            const remainingStr = moment.utc(remainingMsRounded).format("mm:ss");
            if (remainingStr !== this.$el.text()) {
                this.$el.text(remainingStr);
            }
        },
        /**
         * Updates the expiration date by reading from backend
         */
        _refreshExpirationDate: async function () {
            const expireDate = await this._rpc({route: "/shop/cart/get_expire_date"});
            this._setExpirationDate(expireDate);
            const remainingMs = this._getRemainingMs();
            if (remainingMs > 0) {
                this._renderTimer(remainingMs);
                this._startTimer();
                this.$el.show();
            } else {
                this._stopTimer();
                this.$el.hide();
            }
            return this.expireDate;
        },
    });
});
