/* eslint-disable no-undef */
import {App} from "@odoo/owl";
import {PortalChatterService} from "@portal/chatter/frontend/portal_chatter_service";
import {PortalReview} from "@website_sale_dynamic_review_snippet/components/portal_review.esm";
import {_t} from "@web/core/l10n/translation";
import {getTemplate} from "@web/core/templates";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";

patch(PortalChatterService.prototype, {
    async initialize(env) {
        const reviewEl = document.querySelector(".o_portal_reviews");
        if (!reviewEl) {
            return super.initialize(env);
        }
        const reviewSnippet = document.querySelector(".s_customer_review");
        const props = {
            limit:
                parseInt(reviewSnippet.getAttribute("data-max-number-reviews"), 10) ||
                20,
            twoColumns: reviewSnippet.getAttribute("data-two-columns") !== "true",
        };
        this.createShadow(reviewEl).then((shadow) => {
            new App(PortalReview, {
                env,
                getTemplate,
                props,
                translatableAttributes: ["data-tooltip"],
                translateFn: _t,
                dev: env.debug,
            }).mount(shadow);
        });
        const data = await rpc("/portal/review_init", {}, {silent: true});
        this.store.insert(data);
        odoo.portalChatterReady.resolve(true);
    },
});
