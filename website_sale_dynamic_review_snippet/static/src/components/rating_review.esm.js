import {Component, onWillUpdateProps} from "@odoo/owl";

export class RatingReview extends Component {
    static template = "website_sale_dynamic_review_snippet.RatingReview";
    static props = [
        "messages",
        "selectedRating",
        "setStar",
        "resetStars",
        "twoColumns",
    ];

    setup() {
        this.updateRating(this.props.messages);
        onWillUpdateProps((nextProps) => {
            this.updateRating(nextProps.messages);
        });
    }

    updateRating(messages) {
        this.rating = messages
            .map((rate) => rate.rating_value)
            .filter((rateValue) => rateValue >= 1);
        this.ratingTotal = this.rating.reduce(
            (accumulator, currentValue) => accumulator + currentValue,
            0
        );
        const ratingPercent = Object.groupBy(this.rating, (r) => r);
        const ratings = [1, 2, 3, 4, 5];
        ratings.forEach((key) => {
            const value = ratingPercent[key] || [];
            ratingPercent[key] = Math.round((value.length / this.rating.length) * 100);
        });
        this.ratingPercent = ratingPercent;
    }

    get ratingStats() {
        return {
            total: this.rating.length,
            avg: Math.round(this.ratingTotal / this.rating.length),
            percent: this.ratingPercent,
        };
    }

    async onClickStarDomain(star) {
        this.props.setStar(star);
    }

    async onClickStarDomainReset() {
        this.props.resetStars();
    }
}
