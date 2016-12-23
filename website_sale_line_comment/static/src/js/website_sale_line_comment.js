odoo.define('website_sale_line_comment.website_sale_line_comment', function (require) {
'use strict';

	var ajax = require('web.ajax');
	
	$(document).on('change', '#shoping_cart_website_notes', function(){
		ajax.jsonRpc("/shop/shoping_cart_website_notes", 'call', {'line_id': $(this).data('line_id'),'website_note': $(this).val()})
	})
	
})