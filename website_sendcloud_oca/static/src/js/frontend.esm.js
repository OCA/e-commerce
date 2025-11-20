/** @odoo-module */
/* global sendcloud */
import {cookie} from "@web/core/browser/cookie";
import {loadJS} from "@web/core/assets";
import publicWidget from "@web/legacy/js/public/public_widget";
import {renderToString} from "@web/core/utils/render";
import {session} from "@web/session";
import {sprintf} from "@web/core/utils/strings";
const WebsiteSaleDeliverySendcloudWidget = publicWidget.registry.websiteSaleDelivery;

WebsiteSaleDeliverySendcloudWidget.include({
    events: Object.assign(
        {
            "click .o_website_sendcloud_btn": "_onClickSendcloudButton",
            "click .o_website_sendcloud_address": "_onClickSendcloudAddress",
        },
        WebsiteSaleDeliverySendcloudWidget.prototype.events
    ),

    init() {
        this._super.apply(this, arguments);
        loadJS("/delivery_sendcloud_oca/static/src/lib/sendcloud/api.min.js");
    },

    _handleCarrierUpdateResult: async function () {
        await this._super(...arguments);
        // Update view
        var $allSendcloudBtns = this.$el.find(".o_website_sendcloud_btn");
        $allSendcloudBtns.addClass("d-none");
        var $allSendcloudAddr = this.$el.find(".o_website_sendcloud_address");
        $allSendcloudAddr.remove();

        // Show the selected carrier service point button
        var xpath_to_search = sprintf(
            "input[name='delivery_type'][value='%s']",
            this.result.carrier_id
        );
        var $carrierSelect = this.$el.find(xpath_to_search).parent();
        var $sendcloudBtn = $carrierSelect.find("button[name='website_sendcloud_btn']");
        if (!$sendcloudBtn.length) {
            return;
        }
        $sendcloudBtn.removeClass("d-none");
        $sendcloudBtn.data("sendcloud_details", this.result.sendcloud_details);

        // Update sale order
        this.keepLast.add(
            this.rpc("/shop/sendcloud_update_service_point_address", {
                order_id: this.result.sendcloud_details.order_id,
                sendcloud_service_point_address: false,
            })
        );

        // Disable pay button
        var $payButton = this.$('button[name="o_payment_submit_button"]');
        $payButton.attr("disabled", true);
    },

    _onClickSendcloudButton: function (ev) {
        var $btn = $(ev.target);
        var sendcloudDetails = $btn.data("sendcloud_details");

        const availableLanguages = [
            "en-us",
            "de-de",
            "en-gb",
            "es-es",
            "fr-fr",
            "it-it",
            "nl-nl",
        ];
        const lang =
            session.bundle_params.lang || cookie.get("frontend_lang") || "en-us";
        const langIndex = lang
            .replace("_", "-")
            .toLowerCase()
            .indexOf(availableLanguages);
        const selectedLanguage = availableLanguages[langIndex === -1 ? 0 : langIndex];
        const config = {
            apiKey: sendcloudDetails.key,
            country: sendcloudDetails.country_code,
            postalCode: sendcloudDetails.postcode,
            language: selectedLanguage,
            carriers: sendcloudDetails.carrier_name,
        };

        sendcloud.servicePoints.open(
            config,
            this._onServicePointSelected.bind(this, $btn, sendcloudDetails),
            this._onServicePointError.bind(this)
        );
    },

    _onServicePointSelected: function ($btn, sendcloudDetails, servicePoint) {
        // Update view
        this.$(".o_website_sendcloud_address").remove();
        var address = renderToString("website_sendcloud_oca.Address", {
            servicePoint: servicePoint,
        });
        $btn.after(address);

        // Update sale order
        this.keepLast.add(
            this.rpc("/shop/sendcloud_update_service_point_address", {
                order_id: sendcloudDetails.order_id,
                sendcloud_service_point_address: JSON.stringify(servicePoint),
            })
        );

        // Enable pay button
        const $payButton = this.$('button[name="o_payment_submit_button"]');
        $payButton.attr("disabled", false);
    },

    _onServicePointError: function (errors) {
        const irrelevantErrors = ["Closed"];
        var relevantErrors = $(errors).not(irrelevantErrors).get();
        if (relevantErrors.length) {
            // eslint-disable-next-line no-alert
            alert(relevantErrors.join("\n"));
            return;
        }
    },

    _onClickSendcloudAddress: function (ev) {
        ev.stopPropagation();
    },
});
