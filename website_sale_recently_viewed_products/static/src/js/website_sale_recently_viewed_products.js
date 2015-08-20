$(document).ready(function() {
    var _t = openerp._t;
    var product_history_link = $('ul#top_menu li a[href^="/shop/recent"]');
    var product_history_link_counter;

    product_history_link.popover({
        trigger: 'manual',
        animation: true,
        html: true,
        title: function () {
            return _t("Recent Products");
        },
        container: 'body',
        placement: 'auto',
        template: '<div class="popover history-popover" role="tooltip">' +
            '<div class="arrow"></div><h3 class="popover-title"></h3>' +
            '<div class="popover-content"></div></div>'
    }).on("mouseenter",function () {
        var self = this;
        clearTimeout(product_history_link_counter);
        product_history_link.not(self).popover('hide');
        product_history_link_counter = setTimeout(function(){
            if($(self).is(':hover') && !$(".history-popover:visible").length)
            {
                $.get("/shop/recent", {'type': 'popover'})
                    .then(function (data) {
                        $(self).data("bs.popover").options.content =  data;
                        $(self).popover("show");
                        $(".popover").on("mouseleave", function () {
                            $(self).trigger('mouseleave');
                        });
                    });
            }
        }, 100);
    }).on("mouseleave", function () {
        var self = this;
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                if(!$(self).is(':hover'))
                {
                   $(self).popover('hide');
                }
            }
        }, 1000);
    });

});
