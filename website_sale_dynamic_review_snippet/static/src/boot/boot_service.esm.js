/* eslint-disable no-undef */
import {Deferred} from "@web/core/utils/concurrency";
import {loadBundle} from "@web/core/assets";
import {memoize} from "@web/core/utils/functions";
import {registry} from "@web/core/registry";

odoo.portalChatterReady = new Deferred();

const loader = {
    loadChatter: memoize(() => loadBundle("portal.assets_chatter")),
};
export const portalReviewBootService = {
    start() {
        const reviewEl = document.querySelector(".o_portal_reviews");
        if (reviewEl) {
            loader.loadChatter();
        }
    },
};
registry.category("services").add("portal.review.boot", portalReviewBootService);
