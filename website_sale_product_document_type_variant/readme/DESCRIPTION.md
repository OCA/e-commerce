Glue module: keeps the product page's "Documents" section grouped by
document type (added by `website_sale_product_document_type`) after the
customer switches variant (the dynamic refresh added by
`website_sale_product_document_variant`).

Without it, switching variant would still show the correct documents, but
ungrouped, undoing the by-type grouping shown on the initial page load.
