This module is a glue between
[website_sale](https://github.com/odoo/odoo/tree/18.0/addons/website_sale)
and
[sale_order_carrier_auto_assign](https://github.com/OCA/sale-workflow/tree/18.0/sale_order_carrier_auto_assign).

When `sale_order_carrier_auto_assign` is installed with `carrier_on_create`
enabled and a shipping partner has `property_delivery_carrier_id` set, its
`create`/`write` overrides automatically add a delivery line from the partner's
default carrier. On website orders, `website_sale` already handles carrier
selection via `_get_preferred_delivery_method` (which reads
`property_delivery_carrier_id`) and `_set_delivery_method` (which removes any
existing delivery line before adding the new one). Letting both mechanisms run
in parallel creates two delivery lines, causing a
`ValueError: Expected singleton` crash in `order_2_return_dict` at checkout
confirmation.

This module prevents the OCA auto-assign from running on website orders
(`website_id` is set) so that `website_sale` remains the sole owner of
delivery-line management for e-commerce carts.
