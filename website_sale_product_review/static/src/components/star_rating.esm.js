/** Copyright 2025 Kencove - Mohamed Alkobrosli
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

/* global document, console */
import {Component, useRef, useState} from "@odoo/owl";
import {rpc} from "@web/core/network/rpc";

export class StarRating extends Component {
    setup() {
        this.csrfToken = odoo.csrf_token;
        const productIdInput = document.querySelector("input.product_template_id");
        this.productId = productIdInput ? parseInt(productIdInput.value, 10) : null;
        this.reviewComment = useRef("reviewCommentRef");
        this.state = useState({
            rating: 0,
            hover: 0,
            hasText: false,
            readyToSubmit: false,
        });
    }
    setRating(value) {
        if (this.state.rating === value) {
            this.state.rating = 0;
        } else {
            this.state.rating = value;
        }
        this.checkIfReadyToSubmit();
    }
    setHover(value) {
        this.state.hover = value;
    }
    resetHover() {
        this.state.hover = 0;
    }
    checkIfReadyToSubmit() {
        this.state.hasText =
            this.reviewComment && this.reviewComment.el.value.trim().length > 0;
        if (this.state.rating > 0 && this.state.hasText && this.productId) {
            this.state.readyToSubmit = true;
        } else {
            this.state.readyToSubmit = false;
        }
    }
    async onClickSubmit() {
        if (this.state.readyToSubmit) {
            const data = await rpc(`product_review/${this.productId}/post_review`, {
                access_token: this.csrfToken,
                product_id: this.productId,
                rating: this.state.rating,
                comment: this.reviewComment.el.value,
            });
            if (data.error) {
                console.warn(data.message);
            } else {
                this.state.rating = 0;
                this.reviewComment.el.value = "";
                this.state.readyToSubmit = false;
            }
        }
    }
}
