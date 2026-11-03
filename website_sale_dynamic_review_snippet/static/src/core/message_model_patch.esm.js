import {Message} from "@mail/core/common/message_model";

import {patch} from "@web/core/utils/patch";
import {url} from "@web/core/utils/urls";

patch(Message.prototype, {
    setup() {
        super.setup(...arguments);
        this.website_url = "";
    },

    get resUrl() {
        if (this.website_url) return url(this.website_url);
        return super.resUrl;
    },
});
