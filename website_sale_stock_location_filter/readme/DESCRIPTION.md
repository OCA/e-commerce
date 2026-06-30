This module lets you choose, per stock location, whether its on-hand
quantity is counted towards the stock quantity displayed on the website
shop.

By default every internal location contributes to the displayed stock.
Internal locations that should not be shown to website visitors (for
example technician locations) can be flagged with **Exclude from Website
Stock** on the location form; their quantity is then left out of the
quantity shown on product pages.

The displayed quantity keeps using `free_qty` (on hand minus reserved),
exactly as standard Odoo does, restricted to the non-excluded internal
locations of the website's warehouse.
