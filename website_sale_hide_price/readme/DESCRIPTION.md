This module allows to have hidden product prices on the website store.

The prices are also hidden server-side, so they cannot be read from the page
source or the JSON routes. When the price is hidden for the visitor:

- `/website_sale/get_combination_info` returns the prices (and the price sent
  to Google Analytics) as 0.0, with `website_hide_price` set.
- The product JSON-LD markup has no price.
- The product cannot be added to the cart, and the product and combo
  configurators are refused. The product configurator also returns 0.0
  for optional products with a hidden price, and the product is not
  offered as a suggested accessory in the cart.
- The `/shop` price filter and the sorting by price are ignored.
