This module extends the functionality of `sale_order_secondary_unit` to
allow selling products in the online store using the secondary units
defined on the product.

Odoo ships a similar feature based on `uom.uom` records shared by all
products (the *Packagings* field). Secondary units are instead defined
per product and keep both quantities (product unit and secondary unit)
on the sale order line, which is useful when each product has its own
packing sizes.
