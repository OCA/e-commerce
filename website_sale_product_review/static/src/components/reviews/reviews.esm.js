/** Copyright 2025 Kencove - Mohamed Alkobrosli
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {useStore} from "../../store.esm";
import {Component, onWillStart, useState} from "@odoo/owl";
import {rpc} from "@web/core/network/rpc";

export class ProductReviewWidget extends Component {
    static template = "website_sale_product_review.ProductReviewWidget";

    setup() {
        this.store = useStore();
        this.state = useState({
            reviews: [],
            page: 1,
            total: 0,
            pages: 1,
            rating_filter: null,
        });
        onWillStart(async () => {
            await this.loadReviews();
        });
    }

    async loadReviews() {
        const res = await rpc(
            `/shop/product_review/${this.store.productId}/get_reviews`,
            {
                product_id: this.store.productId,
                page: this.state.page,
                rating_filter: this.state.rating_filter,
            }
        );
        this.state.reviews = res.reviews;
        this.state.total = res.total;
        this.state.pages = res.pages;
    }

    onRatingFilterChange(ev) {
        const value = ev.target.value;
        this.state.rating_filter = value === "null" ? null : parseInt(value);
        this.state.page = 1;
        this.loadReviews();
    }

    changePage(p) {
        this.state.page = p;
        this.loadReviews();
    }

    filterByRating(r) {
        this.state.rating_filter = r;
        this.state.page = 1;
        this.loadReviews();
    }

    prevPage() {
        if (this.state.page > 1) {
            this.changePage(this.state.page - 1);
        }
    }

    nextPage() {
        if (this.state.page < this.state.pages) {
            this.changePage(this.state.page + 1);
        }
    }

    get isPrevDisabled() {
        return this.state.page <= 1;
    }

    get isNextDisabled() {
        return this.state.page >= this.state.pages;
    }

    get pageRange() {
        return Array.from({length: this.state.pages}, (_, i) => i + 1);
    }
}
