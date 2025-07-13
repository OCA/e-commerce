/**  Copyright 2025 Kencove (http://www.kencove.com).
     @author Mohamed Alkobrosli <malkobrosly@kencove.com>
     License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). **/

/* global document */
import {patch} from "@web/core/utils/patch";
import {DateSection} from "@mail/core/common/date_section";
import {Message} from "@mail/core/common/message";
import {Thread} from "@mail/core/common/thread";
import {Component, onMounted, onWillStart, useState} from "@odoo/owl";

export class Paginator extends Component {
    static template = "website_sale_customer_reviews.Paginator";
    static components = {DateSection, Message};
    setup() {
        this.state = useState({
            mountedAndLoaded: this.props.mountedAndLoaded,
            currentPage: 1,
        });
        onMounted(() => {
            this.state.mountedAndLoaded = this.props.mountedAndLoaded;
        });
        onWillStart(() => {
            const chatterEl = document.querySelector(".o_portal_chatter");
            this.pageSize = parseInt(chatterEl.getAttribute("data-pager_step", 10));
        });
    }
    get totalPages() {
        const total = this.props.messages.length;
        return Math.floor((total + this.pageSize - 1) / this.pageSize);
    }

    get paginatedMessages() {
        const start = (this.state.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        if (!isNaN(start) && !isNaN(end)) {
            return this.props.messages.slice(start, end);
        }
        return this.props.messages;
    }

    nextPage() {
        if (this.state.currentPage < this.totalPages) {
            this.state.currentPage += 1;
        }
    }

    prevPage() {
        if (this.state.currentPage > 1) {
            this.state.currentPage -= 1;
        }
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.state.currentPage = page;
        }
    }
}

patch(Thread, {
    components: {...Thread.components, Paginator},
});
