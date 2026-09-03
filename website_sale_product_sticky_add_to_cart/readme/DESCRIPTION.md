This module adds a sticky *Add to Cart* bar to the product page of the
e-commerce.

While the visitor scrolls down the page, a fixed bar slides up from the
bottom showing a thumbnail of the product, its name, the current price and
an *Add to Cart* button. The button triggers the standard `website_sale`
add-to-cart flow, so quantity options, bundles and variant behaviour keep
working as usual.

The bar is hidden with a CSS transform, so it never affects page scrolling
or layout. It does not modify the backend and can be turned on and off per
website from the standard *Customize* menu of the product page.
