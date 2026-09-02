Standard Odoo blocks publishing a product document that is attached to a
specific variant instead of the whole product: the "Publish on website"
option is hidden and cannot be enabled for it.

This module lifts that limitation. A document attached to a variant can be
published, is shown on the product page alongside the product's own
documents for whichever variant the customer currently has selected, and
the list refreshes automatically -- without reloading the page -- when the
customer switches variant. The section disappears entirely when the
selected variant has no published document. Downloading such a document is
only allowed while it is published.
