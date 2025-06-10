/** Copyright 2025 Kencove - Mohamed Alkobrosli
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

/* global document */
import {StarRating} from "./components/star_rating.esm";
import {App, loadFile, reactive, whenReady, xml} from "@odoo/owl";
import {templates} from "@web/core/assets";

whenReady(async () => {
    const target = document.querySelector("#star_rating");
    if (target) {
        const xml_temp_1 = await loadFile(
            "website_sale_product_review/static/src/components/star_rating.xml"
        );
        const temp_1 = xml`${xml_temp_1}`;
        const all_templates = reactive({});
        all_templates["website_sale_product_review.StarRating"] = temp_1;
        const env = {store: all_templates};
        StarRating.template = env.store["website_sale_product_review.StarRating"];
        const app = new App(StarRating, {
            templates,
            translatableAttributes: ["data-tooltip"],
            test: false,
            env,
        });
        app.mount(target);
    }
});
