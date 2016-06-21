$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    var checkout_company_name = $(oe_website_sale).find("#checkout_company_name");
    var label_your_name = $(oe_website_sale).find("#label_your_name");
    $(oe_website_sale).on("change", '#partner_type', function (event) {
        var partner_type = $(event.target);
        if (partner_type.val() == "individual"){
            checkout_company_name.show();
            label_your_name.html("Your Name");
        }
        else if (partner_type.val() == "company"){
            checkout_company_name.hide();
            label_your_name.html("Company Name");
        }
        else if (partner_type.val() == "select"){
            checkout_company_name.show();
            label_your_name.html("Your Name");
        }
    });
    $('#partner_type').change();
    });
});
