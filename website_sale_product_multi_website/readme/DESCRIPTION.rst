By default, Odoo allows to set just one (or all) website for products to be
sold on eCommerces, by setting the field product_template.website_ids (a
many2one field). This module allows to set more than one value (website) in
this field (convert it in a many2many field).

When uninstalling this module, if a product is configured for more than a
website, the product will be configured for all websites.
