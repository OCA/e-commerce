// Copyright 2020 Tecnativa - Alexandre Díaz

import options from "@web_editor/js/editor/snippets.options";

options.registry.js_product_category = options.Class.extend({
    /**
     * @override
     */
    cleanForSave: function () {
        this._super(...arguments);
        this.$target.empty();
    },
});
