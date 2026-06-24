This module displays the suggested **Accessory Products** configured on a
product (field `accessory_product_ids` on `product.template`) directly on the
website product detail page.

In standard Odoo, accessory products are only surfaced after a customer adds
the parent product to the cart (in the "Suggested accessories" block of the
cart page). This module brings the same suggestions one step earlier in the
funnel by rendering them on the product page itself, encouraging cross-sell
while the customer is still researching the main product.

The same filtering rules used by the cart suggestion logic are applied:
unpublished products, products outside the current company, products without
quick-add support, and zero-priced products (when the website forbids
zero-price sale) are excluded.
