odoo.define("website_sale_one_step_checkout.osc", function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var Widget = require('web.Widget');

    var OneStepCheckout = Widget.extend({
            init: function () {
                this._super();
            },
            start: function () {
                var self = this;

                // activate event listener
                self.changeShipping();
                self.hideShow();

                // Editing Billing Address
                $('.js-billing-address .js_edit_address').on('click',
                    function (e) {
                        self.editBilling(null, self, e)
                    });

                // Editing shipping address
                $('.js-shipping-address .js_edit_address').on('click', function (e) {
                    self.editShipping(self, e)
                });

                // Add new shipping address
                $("#add-shipping-address").on('click', 'a, input', function (e) {
                    self.addShipping(self, e)
                });

                $('#address-modal').on('click', '#js_confirm_address', function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    // Upon confirmation, validate data.
                    self.validateModalAddress();
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

                    self.checkData().then(function (result) {
                        if (result.success) {
                            // proceed to payment transaction
                            self.proceedPayment(ev);
                        } else {
                            return false;
                            // do nothing, address modal in edit mode
                            // will get automatically opened at this point
                        }
                    });
                    return false;
                });
            },
            proceedPayment: function (event) {
                var self = this;
                ajax.jsonRpc('/shop/checkout/proceed_payment/', 'call', {}).then(function (errors) {
                    //TODO errors
                    if (errors) {
                        console.log(errors)
                    }
                    var $form = $(event.currentTarget).parents('form');
                    var acquirer_id = $(event.currentTarget).parents('div.oe_sale_acquirer_button').first().data('id');
                    if (!acquirer_id) {
                        return false;
                    }
                    $form.off('submit');
                    self.startTransaction(acquirer_id);
                });
            },
        displayFormErrors: function (errors) {
            var selector = '.oe_website_sale_osc';
            for (var key in errors) {
                if ($(selector + ' input[name=' + key + ']').length > 0) {
                    $(selector + ' input[name=' + key + ']').parent().addClass('has-error');
                } else if ($(selector + ' select[name=' + key + ']').length > 0) {
                    $(selector + ' select[name=' + key + ']').parent().addClass('has-error');
                }
            }
        },
            removeErrors: function () {
                // If the user leaves the modal after a wrong input and
                // and opens the add-billing-address modal, those
                // fields will be still highlighted red.
                $('.oe_website_sale_osc .has-error').removeClass('has-error');
            },
        getPostFields: function (elms, data) {
            elms.each(function () {
                    var key = $(this).attr('name');
                    var val = $(this).val();
                if (key in data && key === 'field_required') {
                        // In case of shipping address by the public user
                        // we will retrieve `field_required` twice,
                        // both for billing and shipping fields
                        // In this case we don't want to override but
                        // merge the required fields.
                        data[key] += ',' + val;
                    } else {
                        data[key] = val;
                    }
                });
                return data;
            },
            validateModalAddress: function () {
                var self = this;
                var formElems = $('#osc-modal-form input, #osc-modal-form select'),
                    data = {};

                data = self.getPostFields(formElems, data);

                // For validation we need `submitted`
                data.submitted = true;

                $('.oe_website_sale_osc .has-error').removeClass('has-error');

                ajax.jsonRpc('/shop/checkout/render_address/', 'call', data).then(function (result) {
                    if (result.success) {
                        $('#js_confirm_address').attr("disabled", false);

                        // Update frontend address view
                        $('#col-1').html(result.template);

                        // Re-enable JS event listeners
                        $('.js-billing-address .js_edit_address').on('click', function (e) {
                            self.editBilling(null, self, e)
                        });
                        $('.js-shipping-address .js_edit_address').on('click', function (e) {
                            self.editShipping(self, e)
                        });
                        $("#add-shipping-address").on('click', 'a', function (e) {
                            self.addShipping(self, e)
                        });
                        self.changeShipping();

                        // hide Modal
                        $('#address-modal').modal('hide');
                    } else if (result.errors) {
                        if (result.errors.error_message) {
                            $(".text-danger").remove();
                            var $name = $('.checkout_autoformat > .div_name');
                            var prefix = '<h5 class="text-danger">';
                            var suffix = '</h5>';
                            $(result.errors.error_message).each(function () {
                                $name.prepend(
                                    prefix + this + suffix
                                )
                            })
                        }
                        self.displayFormErrors(result.errors);
                    } else {
                        // ???
                        window.location.href = '/shop';
                    }
                });
            },
            startTransaction: function (acquirer_id) {
                ajax.jsonRpc('/shop/payment/transaction/' + acquirer_id, 'call', {}).then(function (data) {
                    $(data).appendTo('body').submit();
                });
                return false;
            },
        validateBillingInfo: function () {
                // Helper function for validating public user account info
            $('.oe_website_sale_osc .has-error').removeClass('has-error');

                var self = this;
            var billingFormElems = $('#public-billing-address input, #public-billing-address select'),
                shippingFormElems = $('#public-shipping-address input, #public-shipping-address select'),
                    data = {};
                data.submitted = true;

            // get billing data
            data = self.getPostFields(billingFormElems, data);

            // if checkbox is not checked, get shipping address
            if (!$('input[name=public_shipping]:checked').length) {
                data = self.getPostFields(shippingFormElems, data);
                data['delivery_address'] = true
            }

                return ajax.jsonRpc('/shop/checkout/render_address/', 'call', data).then(function (result) {
                    if (result.success) {
                        return result;
                    } else {
                        if (result.errors.error_message) {
                            $(".text-danger").remove();
                            var $name = $('.oe_website_sale_osc > .row');
                            var prefix = '<h4 class="text-danger">';
                            var suffix = '</h4>';
                            $(result.errors.error_message).each(function () {
                                $name.prepend(
                                    prefix + this + suffix
                                )
                            })
                        }
                        self.displayFormErrors(result.errors);
                        return {'success': false}
                    }
                });
            },
            checkData: function () {
                var self = this;
                var create_account = $("#create-account").length;

                // Public users
                if (create_account && $("#create-account").is(':visible')) {
                    return self.validateBillingInfo().done(function (result) {
                        if (result.success) {
                            return self.validateCheckoutData();
                        } else {
                            // do nothing, errors will be displayed
                        }
                    });
                } else {  // Logged in users
                    return self.validateCheckoutData();
                }
            },
            validateCheckoutData: function () {
                // Helper function to validate checkout data
                // This function validates the mandatory billing fields
                // if everything is fine return success
                // else open the billing address form / modal
                var self = this;
                return ajax.jsonRpc('/shop/checkout/validate_checkout_data', 'call', {}).then(function (result) {
                    if (result.success) {
                        return result;
                    } else {
                        // if public user open form automatically
                        var checkout_guest = $('input[name=public_customer]')[1];
                        if (checkout_guest) {
                            $(checkout_guest).click()
                        } else {
                            // if logged in customer open modal
                            self.editBilling(result, self);
                        }
                        return result;
                    }
                });
            },
            hideShow: function () {
                // radio buttons: login / checkout as guest
                $('#public_acc_info input[type="radio"]').click(function () {
                    if ($(this).val() == '1') {
                        $('#log-in').show();
                        $('#create-account').hide();
                    }
                    else {
                        $('#log-in').hide();
                        $('#create-account').show();
                    }
                });

                // checkbox: public user shipping address
                $('input[name="public_shipping"]').change(function () {
                    if ($(this).is(':checked')) {
                        $("#public-shipping-address").hide()
                    }
                    else {
                        $("#public-shipping-address").show()
                    }
                });
            }
            ,
            renderModal: function (data) {
                // Render address template into modal body
                return ajax.jsonRpc('/shop/checkout/render_address/', 'call', data).then(function (result) {
                    $('#address-modal').modal('show');
                    if (result.success) {
                        $('#address-modal .modal-header h4').html(result.modal_title);
                        $('#address-modal .modal-body').html(result.template);

                        // Display states if existent for selected country, e.g. US
                        $("select[name='country_id']").change();
                    }
                });
            },
            changeShipping: function () {
                // from website_sale.js
                $('#osc_shipping').on('click', '.js_change_shipping', function () {
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
                        $.post($form.attr('action'), $form.serialize() + '&xhr=1');
                    }
                });
            }
            ,
            editBilling: function (result, self, e) {
                // If the user leaves the modal after a wrong input and
                // and opens the add-billing-address modal, those
                // fields will be still highlighted red.
                self.removeErrors();

                var partner_id = null;

                if (result && result.partner_id) {
                    // This argument will be
                    // returned by the controller validate_checkout_data
                    // after its call from the validateCheckoutData function.
                    // It's necessary in the situation where there exists
                    // a name and e-mail from the sign-up procedure, but no
                    // further mandatory billing data. This will trigger the
                    // modal in "Edit Billing Address" mode.
                    partner_id = result.partner_id;
                } else {
                    partner_id = $(e.currentTarget).siblings('form').find('input[name=partner_id]').val();
                }

                var data = {
                    'modal_title': 'Billing Address',
                    'partner_id': partner_id,
                };

                self.renderModal(data);
            }
            ,
            editShipping: function (self, e) {
                // If the user leaves the modal after a wrong input and
                // and opens the add-billing-address modal, those
                // fields will be still highlighted red.
                $('.oe_website_sale_osc .has-error').removeClass('has-error');

                var partner_id = $(e.currentTarget).siblings('form').find('input[name=partner_id]').val();

                var data = {
                    'modal_title': 'Shipping Address',
                    'partner_id': partner_id,
                };

                self.renderModal(data);
            },
            addShipping: function (self, e) {
                // If the user leaves the modal after a wrong input and
                // and opens the add-billing-address modal, those
                // fields will be still highlighted red.
                $('.oe_website_sale_osc .has-error').removeClass('has-error');

                var data = {
                    'modal_title': 'Shipping Address',
                };

                self.renderModal(data);
            }
        })
    ;


    base.dom_ready.done(function () {
        var osc = new OneStepCheckout();
        osc.start();
    });

    return OneStepCheckout;
});