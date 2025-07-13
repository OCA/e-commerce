/**  Copyright 2025 Kencove (http://www.kencove.com).
     @author Mohamed Alkobrosli <malkobrosly@kencove.com>
     License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). **/

/* global Chart */
import {patch} from "@web/core/utils/patch";
import {Chatter} from "@mail/chatter/web_portal/chatter";
import {loadJS} from "@web/core/assets";
import {getColor} from "@web/core/colors/colors";
import {rpc} from "@web/core/network/rpc";
import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";

export class BarChart extends Component {
    static template = "website_sale_customer_reviews.BarChart";
    setup() {
        this.rpc = rpc;
        this.canvasRef = useRef("canvas");
        this.state = useState({
            avg: null,
            total: null,
        });
        onWillStart(() => {
            return loadJS(["/web/static/lib/Chart/Chart.js"]);
        });
        onMounted(async () => {
            const url =
                "/customer_review/product_template/stats/" + this.props.threadId;
            this.ratings = await this.rpc(url);

            if (this.ratings && this.ratings.avg && this.ratings.total) {
                this.callChart();
            }
        });
        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }
    callChart() {
        if (this.props.threadModel && this.props.threadId) {
            if (this.chart) {
                this.chart.destroy();
            }
            this.renderChart();
        }
    }
    renderChart() {
        const ratings = this.ratings;
        const labels = ratings?.percent ? Object.keys(ratings.percent) : [];
        const data = ratings?.percent ? Object.values(ratings.percent) : [];
        const color = labels.map((_, index) => {
            return getColor(index);
        });
        const avg = typeof ratings?.avg === "number" ? ratings.avg : null;
        this.state.avg = Math.round(avg * 10) / 10;
        this.state.total = typeof ratings?.total === "number" ? ratings.total : null;

        this.chart = new Chart(this.canvasRef.el, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Ratings",
                        data: data,
                        backgroundColor: color,
                    },
                ],
            },
            options: {
                indexAxis: "y", // Make bars horizontal
                plugins: {
                    legend: {
                        display: false, // Hide legend if not needed
                    },
                    tooltip: {
                        enabled: true, // Keep tooltips for interactivity
                    },
                },
                scales: {
                    x: {
                        grid: {
                            display: false, // Remove vertical grid lines
                        },
                        ticks: {
                            display: false, // Hide X axis labels
                        },
                        border: {
                            display: false, // Remove X axis line
                        },
                    },
                    y: {
                        grid: {
                            display: false, // Remove horizontal grid lines
                        },
                        ticks: {
                            color: "#333", // Optional: Make Y labels dark
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        border: {
                            display: false, // Remove Y axis line
                        },
                    },
                },
            },
        });
    }
}

patch(Chatter, {
    components: {...Chatter.components, BarChart},
});
