odoo.define("website_sale_infinite_scroll.main", function (require) {
    "use strict";

    var sAnimations = require("website.content.snippets.animation");
    var core = require("web.core");
    var _t = core._t;

    sAnimations.registry.infinite_scroll = sAnimations.Class.extend({
        selector: "#wrapwrap",
        allow_load: true,
        flag: true,
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            // Parse current page number and compute next one
            var current_url = window.location.pathname;

            if (current_url.indexOf("/shop") !== -1 && self._check_pagination()) {
                var current_arguments = window.location.search;
                self.current_page = 1;
                if (current_url.indexOf("/page") === -1) {
                    current_url = current_url.replace(
                        "/shop",
                        "/shop/page/" + self.current_page
                    );
                }
                var match = current_url.match(/\/page\/(\d*)/);
                self.current_page = match[1];
                current_url = current_url.replace("/page/" + self.current_page, "");
                self.next_page = self.current_page;
                // Build fetch endpoint url
                self.fetch_url =
                    current_url.replace("/shop", "/website_sale_infinite_scroll") +
                    "/page/" +
                    self.next_page +
                    current_arguments;
            }
        },

        start: function () {
            var current_url = window.location.pathname;
            if (current_url.indexOf("/shop") !== -1) {
                var self = this;
                const container = this.el;
                let lastScrollTop = 0;
                const btnBackToTop = document.querySelector(".btn-back-to-top");
                container.addEventListener("scroll", () => {
                    const scrollTop = container.scrollTop;
                    if (self._check_pagination() && scrollTop > lastScrollTop) {
                        if (btnBackToTop && self.flag) {
                            btnBackToTop.classList.remove("d-none");
                        }
                        self._onScroll();
                    }
                    lastScrollTop = scrollTop;
                });
            }
        },
        _check_pagination: function () {
            var pagination = document.querySelector(".products_pager .pagination");
            if (!pagination) return false;
            var style = window.getComputedStyle(pagination).display;
            return style === "none";
        },

        load_next_page: function () {
            var self = this;
            if (self.flag) {
                self.next_page++;
                // Set page in fetch url
                var url = self.fetch_url.replace(
                    "/page/" + self.current_page,
                    "/page/" + self.next_page
                );

                // Add spinner
                var $spinner = $("<span/>", {
                    class: "website_sale_infinite_scroll-spinner",
                    text: _t("Loading more products..."),
                });

                const postData = {
                    csrf_token: core.csrf_token,
                };
                $.ajax({
                    url,
                    success: function (table) {
                        if (table && table !== "") {
                            // Self.$("tbody").append(table);
                            self.$("tbody").html(table);
                        } else {
                            self.flag = false;
                        }
                    },
                    // Error: edialog,
                    // shows the loader element before sending.
                    beforeSend: function () {
                        self.allow_load = false;
                        const date = new Date();
                        $spinner.css(
                            "background",
                            `url(/infinite_scroll_preloader?new=${date.getTime()}) center top no-repeat`
                        );
                        self.$el
                            .find(".o_wsale_products_grid_table_wrapper")
                            .append($spinner);
                    },
                    // Hides the loader after completion of request, whether successfull or failor.
                    complete: function () {
                        self.allow_load = true;
                        self.$el.find(".website_sale_infinite_scroll-spinner").remove();
                    },
                    type: "POST",
                    dataType: "html",
                    data: postData,
                });
            }
        },

        _onScroll: function () {
            var self = this;
            if (self.allow_load) {
                self.load_next_page();
            }
        },
    });
});
