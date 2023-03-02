- This feature doesn't support multi website. The default behavior is to hide the prices
  along every website. It could be modified the boolean field on the partner to a many2many
  relation between res_partner and website_website, so that this price-hiding feature might
  be made website-dependant.
- This module is incompatible with the website_sale_stock_force_block module because it
  makes changes to the same attributes in the website_sale.products_add_to_cart template.
