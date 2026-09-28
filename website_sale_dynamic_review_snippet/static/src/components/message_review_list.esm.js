import {Component, useSubEnv} from "@odoo/owl";
import {MessageReview} from "@website_sale_dynamic_review_snippet/components/message_review.esm";
import {_t} from "@web/core/l10n/translation";

export class MessageReviewList extends Component {
    static template = "website_sale_dynamic_review_snippet.MessageReviewList";
    static components = {MessageReview};

    static props = ["messages", "loadMore?", "onLoadMoreVisible?"];

    setup() {
        super.setup();
        useSubEnv({
            displayRating: false,
            inFrontendPortalChatter: true,
        });
    }

    get messages() {
        return this.props.messages;
    }

    get emptyText() {
        return _t("No messages found");
    }

    async loadMore() {
        this.props.onLoadMoreVisible?.();
    }
}
