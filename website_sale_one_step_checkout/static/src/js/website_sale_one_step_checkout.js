odoo.define("website_sale_one_step_checkout", function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var base = require('web_editor.base');

    function removeErrors(){
        // If the user leaves the modal after a wrong input and
        // and opens the add-billing-address modal, those
        // fields will be still highlighted red.
        $('.oe_website_sale_osc .has-error').removeClass('has-error');
    }

    function getPostAddressFields(elms, data) {
        elms.each(function(index) {
            data[$(this).attr('name')] = $(this).val();
        });
        return data;
    }

    function validateModalAddress(){
        var formElems = $('#osc-modal-form input, #osc-modal-form select'),
            data = {};

        data = getPostAddressFields(formElems, data);

        // For validation we need `submitted`
        data.submitted = true;

        $('.oe_website_sale_osc .has-error').removeClass('has-error');

        ajax.jsonRpc('/shop/checkout/render_address/', 'call', data).
            then(function (result) {
                if (result.success) {
                    $('#js_confirm_address').attr("disabled", false);

                    // Update frontend address view
                    $('#col-1').html(result.template);

                    // Re-enable JS event listeners
                    $('.js-billing-address .js_edit_address').on('click', editBilling);
                    $('.js-shipping-address .js_edit_address').on('click', editShipping);
                    $("#add-shipping-address").on('click', 'a', addShipping);
                    changeShipping();

                    // hide Modal
                    $('#address-modal').modal('hide');
                } else if (result.errors) {
                    for (var key in result.errors) {
                        if ($('.oe_website_sale_osc input[name=' + key + ']').length > 0) {
                            $('.oe_website_sale_osc input[name=' + key + ']').parent().addClass('has-error');
                        } else if ($('.oe_website_sale_osc select[name=' + key + ']').length > 0) {
                            $('.oe_website_sale_osc select[name=' + key + ']').parent().addClass('has-error');
                        }
                    }
                } else {
                    // ???
                    window.location.href = '/shop';
                }
            });
    }

    function startTransaction(acquirer_id){
        ajax.jsonRpc('/shop/payment/transaction/' + acquirer_id, 'call', {}).then(function (data) {
            $(data).appendTo('body').submit();
        });
        return false;
    }

    function validateAddressForm(){
        return ajax.jsonRpc('/shop/checkout/validate_address_form', 'call', {}).then(function (result){
            if(result.success){
                return result;
            } else{
                editBilling(result);
                return result;
            }
        });
    }

    // For Public User
    function addPublicUserAddress() {
        // If the user leaves the modal after a wrong input and
        // and opens the add-billing-address modal, those
        // fields will be still highlighted red.
        removeErrors();


        var data = {
            'modal_title':'Billing Address',
        };

        renderModal(data);
    }

    function renderModal(data){
        // Render address template into modal body
        ajax.jsonRpc('/shop/checkout/render_address/', 'call', data).
            then(function(result) {
                $('#address-modal').modal('show');
                if(result.success) {
                    $('#address-modal .modal-header h4').html(result.modal_title);
                    $('#address-modal .modal-body').html(result.template);

                    // Display states if existent for selected country, e.g. US
                    $("select[name='country_id']").change();
                }
            });
    }

    function changeShipping(){
        // from website_sale.js
        $('#osc_shipping').on('click', '.js_change_shipping', function() {
            if (!$('body.editor_enable').length) {
                //allow to edit button text with editor
                var $old = $('.all_shipping').find('.panel.border_primary');
                $old.find('.btn-ship').toggle();
                $old.addClass('js_change_shipping');
                $old.removeClass('border_primary');

                var $new = $(this).parent('div.one_kanban').find('.panel');
                $new.find('.btn-ship').toggle();
                $new.removeClass('js_change_shipping');
                $new.addClass('border_primary');

                var $form = $(this).parent('div.one_kanban').find('form.hide');
                $.post($form.attr('action'), $form.serialize()+'&xhr=1');
            }
        });
    }

    // Edit Billing Address
    function editBilling(result) {
        // If the user leaves the modal after a wrong input and
        // and opens the add-billing-address modal, those
        // fields will be still highlighted red.
        removeErrors();

        var partner_id = null;

        if(result.partner_id) {
            // This argument will be
            // returned by the controller validate_address_form
            // after its call from the validateAddressForm JS function below.
            // It's necessary in the situation where there exist
            // a name and e-mail from the sign-up procedure, but no
            // further mandatory billing data. This will trigger the
            // modal in "Edit Billing Address" mode.
            partner_id = result.partner_id;
        } else{
            partner_id = $(this).siblings('form').find('input[name=partner_id]').val();
        }

        var data = {
                'modal_title': 'Billing Address',
                'partner_id':partner_id,
            };

        renderModal(data);
    }

    // Edit Shipping Address
    function editShipping () {
        // If the user leaves the modal after a wrong input and
        // and opens the add-billing-address modal, those
        // fields will be still highlighted red.
        $('.oe_website_sale_osc .has-error').removeClass('has-error');

        var partner_id = $(this).siblings('form').find('input[name=partner_id]').val();

        var data = {
            'modal_title': 'Shipping Address',
            'partner_id':partner_id,
        };

        renderModal(data);
    }

    // Add New Shipping Address
    function addShipping() {
        // If the user leaves the modal after a wrong input and
        // and opens the add-billing-address modal, those
        // fields will be still highlighted red.
        $('.oe_website_sale_osc .has-error').removeClass('has-error');

        var data = {
            'modal_title':'Shipping Address',
        };

        renderModal(data);
    }

    base.dom_ready.done(function () {
        // activate event listener
        changeShipping();

        // Automatically open modal in 'Billing address' mode for public user
        $('#add-public-user-address').on('click', addPublicUserAddress);

        // Editing Billing Address
        $('.js-billing-address .js_edit_address').on('click', editBilling);

        // Editing shipping address
        $('.js-shipping-address .js_edit_address').on('click', editShipping);

        // Add new shipping address
        $("#add-shipping-address").on('click', 'a', addShipping);

        $('#address-modal').on('click', '#js_confirm_address', function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            // Upon confirmation, validate data.
            validateModalAddress();
            return false;
        });

        // when choosing an acquirer, display its order now button
        var $payment = $('#payment_method');
        $payment.on('click', 'input[name="acquirer"]', function (ev) {
            var payment_id = $(ev.currentTarget).val();
            $('div.oe_sale_acquirer_button[data-id]').addClass('hidden');
            $('div.oe_sale_acquirer_button[data-id="' + payment_id + '"]').removeClass('hidden');
        }).find('input[name="acquirer"]:checked').click();

        // when clicking checkout submit button validate address data first
        // if all is fine trigger payment transaction
        $('#col-3 .js_payment').on('click', 'form button[type=submit]', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            validateAddressForm().
                then(function (result) {
                    if(result.success){
                        // proceed to payment transaction
                        ajax.jsonRpc('/shop/checkout/proceed_payment/', 'call', {}).
                            then(function (){
                                var $form = $(ev.currentTarget).parents('form');
                                var acquirer_id = $(ev.currentTarget).parents('div.oe_sale_acquirer_button').first().data('id');
                                if (! acquirer_id ){
                                    return false;
                                }
                                $form.off('submit');
                                startTransaction(acquirer_id);
                            });
                    } else{
                        return false;
                        // do nothing, address modal in edit mode
                        // will get automatically opened at this point
                    }
                });
            return false;
        });
    });
});