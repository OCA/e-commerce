odoo.define("website_sale_commitment_date.checkout", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var core = require("web.core");
    const QWeb = core.qweb;
    var concurrency = require("web.concurrency");
    var dp = new concurrency.DropPrevious();

    publicWidget.registry.websiteSaleDelivery =
        publicWidget.registry.websiteSaleDelivery.extend({
            events: _.extend(
                {},
                publicWidget.registry.websiteSaleDelivery.prototype.events,
                {
                    "click .o_website_calendar_confirm": "_onClickCalendarConfirm",
                    "click .o_website_calendar_button": "_onClickCalendarButton",
                    "click .o_website_calendar_next": "_onClickCalendarNext",
                    "click .o_website_calendar_prev": "_onClickCalendarPrev",
                    "click .o_website_calendar_day": "_onClickCalendarDay",
                }
            ),

            _onClickCalendarConfirm: function (ev) {
                ev.preventDefault();
                const $selected = $(".selected");
                dp.add(
                    this._rpc({
                        route: "/shop/update_commitment_date",
                        params: {
                            date: $selected.data("date"),
                        },
                    })
                ).then(this._handleUpdateCommitmentDate.bind(this));
            },

            _handleUpdateCommitmentDate: function (result) {
                const $payment_button = $("button[name='o_payment_submit_button']");
                const $commitment_input = $("input.o_commitment_date_input");
                if (result.success) {
                    $(".o_calendar_modal").modal("hide");
                    $commitment_input.val(result.date);
                    $payment_button.show();
                }
            },

            _onClickCalendarDay: function (ev) {
                ev.preventDefault();
                if ($(ev.currentTarget).data("disabled")) return;

                if ($(ev.currentTarget).hasClass("selected")) {
                    $(ev.currentTarget).removeClass("selected bg-primary text-white");
                    return;
                }
                $(".selected").removeClass("selected bg-primary text-white");
                $(ev.currentTarget).addClass("selected bg-primary text-white");
            },

            _onClickCalendarNext: function (ev) {
                ev.preventDefault();
                dp.add(
                    this._rpc({
                        route: "/calendar/commitment_date",
                        params: {
                            action: "next",
                            start: $(ev.currentTarget).data("start"),
                        },
                    })
                ).then(this._handleCalendarModal.bind(this));
            },
            _onClickCalendarPrev: function (ev) {
                ev.preventDefault();
                dp.add(
                    this._rpc({
                        route: "/calendar/commitment_date",
                        params: {
                            action: "prev",
                            start: $(ev.currentTarget).data("start"),
                        },
                    })
                ).then(this._handleCalendarModal.bind(this));
            },

            _onClickCalendarButton: function (ev) {
                ev.preventDefault();
                dp.add(
                    this._rpc({route: "/calendar/commitment_date", params: {}})
                ).then(this._handleCalendarModal.bind(this));
            },

            _handleCalendarModal: function (result) {
                if (result) {
                    $(".o_website_calendar").html(
                        QWeb.render(
                            "website_sale_commitment_date.WebsiteCalendar",
                            result
                        )
                    );
                    $(".o_calendar_modal").modal("show");
                }
            },

            _handleCarrierUpdateResult: function (result) {
                const $commitment_date = $("#commitment_date");
                const $payment_button = $("button[name='o_payment_submit_button']");
                if (result.allow_commitment_date) {
                    $commitment_date.show();
                    $payment_button.hide();
                } else {
                    $commitment_date.hide();
                    $payment_button.prop("disabled", false);
                }
                this._super.apply(this, arguments);
            },
        });
});
