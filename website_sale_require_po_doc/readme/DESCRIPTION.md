When the `sale_require_po_doc` module is installed, customers flagged as
requiring a Purchase Order number cannot have their sales order confirmed
without a value in the **Customer Reference** field. However, the standard
`website_sale` checkout provides no UI for this field, causing an error page
at the payment step.

This module fills that gap: it injects a **PO Number / Customer Reference**
field on the `/shop/payment` page whenever the current customer has
**Customer Requires PO** enabled.
