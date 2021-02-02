* This module links templates together. 'product_multi_link' links variants
  together. We could, in a next version of Odoo, include variants features
  in that module, and adding a new group in 'Manage Product Variant Links'.

* Develop another module product_template_multi_link_customer, that adds
  a new type of link named 'customer'. Those links could be generated
  automatically by scheduled cron task, analyzing sale.order.line.
  Odoo could create so, the 3 most products sold when a given product is
  sold.
