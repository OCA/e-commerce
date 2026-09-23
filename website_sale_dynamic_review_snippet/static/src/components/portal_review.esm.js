import {Component, onWillStart, useState} from "@odoo/owl";
import {MessageReviewList} from "@website_sale_dynamic_review_snippet/components/message_review_list.esm";
import {OverlayContainer} from "@web/core/overlay/overlay_container";
import {RatingReview} from "@website_sale_dynamic_review_snippet/components/rating_review.esm";
import {rpc} from "@web/core/network/rpc";
import {useService} from "@web/core/utils/hooks";

export class PortalReview extends Component {
    static template = "website_sale_dynamic_review_snippet.PortalReview";
    static components = {RatingReview, MessageReviewList, OverlayContainer};
    static props = ["limit", "twoColumns"];
    setup() {
        this.store = useState(useService("mail.store"));
        this.overlayService = useService("overlay");
        this.state = useState({
            selectedRating: false,
            messages: [],
            searchedMessage: [],
            loadMore: false,
        });
        onWillStart(async () => {
            this.state.messages = await this.fetchMessages();
            await this.updateThread();
            this.state.searchedMessage = this.state.messages;
            this.state.loadMore = true;
            $(".o_portal_reviews_loader").addClass("d-none");
        });
    }

    async updateThread() {
        for (const thread of Object.values(this.store.Thread.records)) {
            await thread.fetchMessages();
        }
    }

    async fetchMessages({after, around, before} = {}) {
        const {data, messages} = await this.fetchMessagesData({after, around, before});
        this.store.insert(data, {html: true});
        odoo.portalChatterReady.resolve(true);
        return this.store.Message.insert(messages);
    }

    async fetchMessagesData({after, around, before} = {}) {
        return await rpc("/mail/review/messages", {
            limit: this.props.limit || 20,
            after,
            around,
            before,
        });
    }

    async setStar(star) {
        this.state.selectedRating = star;
        this.state.searchedMessage = this.state.messages.filter(
            (item) => item.rating_value === parseInt(star, 10)
        );
    }

    async resetStars() {
        this.state.selectedRating = false;
        this.state.searchedMessage = this.state.messages;
    }

    async onLoadMoreVisible() {
        const res = await this.fetchMessages({before: this.state.messages.at(-1).id});
        if (res.length === 0) {
            this.state.loadMore = false;
        } else {
            this.state.messages = this.state.messages.concat(res);
            this.state.searchedMessage = this.state.searchedMessage.concat(res);
        }
    }
}
