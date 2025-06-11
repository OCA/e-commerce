/** Copyright 2025 Kencove - Mohamed Alkobrosli
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

/* global document */
import {StarRating} from "./components/review_form/review_form.esm";
import {ProductReviewWidget} from "./components/reviews/reviews.esm";
import {App, Component, loadFile, reactive, whenReady, xml} from "@odoo/owl";
import {templates} from "@web/core/assets";

export class ReviewRoot extends Component {
    static components = {
        StarRating,
        ProductReviewWidget,
    };
    static template = xml`
    <StarRating/>
    <ProductReviewWidget/>
    `;
}

const all_templates = [
    {
        path: "product_review/portal/static/src/components/review_form/review_form.xml",
    },
    {
        path: "product_review/portal/static/src/components/reviews/reviews.xml",
    },
];

async function loadAndAssignTemplates() {
    for (const template of all_templates) {
        const xml_templ = await loadFile(template.path);
        if (xml_templ.trimStart().startsWith('<templates xml:space="preserve">')) {
            const match = xml_templ.match(/<t\s+[^>]*t-name="([^"]+)"/);
            if (match[1]) {
                template.name = match[1];
                const templ_id = xml`${xml_templ}`;
                template.id = templ_id;
            }
        }
    }
    for (const component of Object.values(ReviewRoot.components)) {
        const swapNameId = all_templates.find((t) => t.name === component.template);
        if (swapNameId) {
            component.template = swapNameId.id;
        }
    }
    return true;
}

whenReady(async () => {
    const productIdInput = document.querySelector("input.product_template_id");
    const productId = productIdInput ? parseInt(productIdInput.value, 10) : null;
    const target = document.querySelector("#star_rating");
    if (target && productId) {
        await loadAndAssignTemplates();
        const store = reactive({
            all_templates: [],
            productId,
        });
        const env = {store};
        const app = new App(ReviewRoot, {
            templates,
            translatableAttributes: ["data-tooltip"],
            test: false,
            env,
        });
        app.mount(target);
    }
});
