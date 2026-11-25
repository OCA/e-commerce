- This module is incompatible with the website_sale_stock_force_block
  module because it makes changes to the same attributes in the
  website_sale.products_add_to_cart template.
- The `/shop` price filter and sorting are only ignored when the prices are
  hidden for the whole website or the visitor, not when only some products
  hide their price.
- Other routes that send prices, such as the product matrix of
  `website_sale_product_matrix` or the Google Merchant Center feed, are not
  covered.
