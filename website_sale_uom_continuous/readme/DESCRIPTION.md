Allows to sell decimal quantities of products in continuous units of measure
(kg, L, m, ...) on the eCommerce.

By default, Odoo casts the quantities added to the cart to integers, so a
customer can't buy 2.5 kg of a product. With this module, quantities are rounded
according to the unit of measure:

- Continuous units of measure keep the decimals allowed by the "Product Unit"
  decimal precision, e.g. 2.5 kg.
- Units of measure based on Units can't be split, and keep integer quantities.

This applies to the product page, the product configurator and the cart.

The cart quantity shown in the header counts each line in a continuous unit of
measure as a single item, e.g. 2.5 kg and 3 units count as 4 items.
