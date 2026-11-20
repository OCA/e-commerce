import {PortalHomeCounters} from "@portal/interactions/portal_home_counters";
import {patch} from "@web/core/utils/patch";

patch(PortalHomeCounters.prototype, {
    /**
     * @override
     */
    getCountersAlwaysDisplayed() {
        return super
            .getCountersAlwaysDisplayed(...arguments)
            .concat(["my_regular_products_count"]);
    },
});
