/** Copyright 2025 Kencove - Mohamed Alkobrosli
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {Component, useState} from "@odoo/owl";

export class StarRating extends Component {
    setup() {
        this.state = useState({
            rating: 0,
            hover: 0,
        });
    }
    setRating(value) {
        if (this.state.rating == value) {
            this.state.rating = 0;
        } else {
            this.state.rating = value;
        }
    }
    setHover(value) {
        this.state.hover = value;
    }
    resetHover() {
        this.state.hover = 0;
    }
}
