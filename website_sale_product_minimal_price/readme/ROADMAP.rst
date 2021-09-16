* When there are some variants with the same minimal price, we won't get the expected
  attribute value sequence order to get the first combination but the default
  `product.product` order. This is like this because we stretch the possible variants
  to a single one which is the first to hit the minimum price. The next ones are
  ignored.

  A way to solve this would be to redisign the `_get_cheapest_info` to get all the
  variants that meet the cheapest found price and return a recordset and then try
  to rely on `super()` to get the first possible combination for those. Some refactor
  would be needed though.
