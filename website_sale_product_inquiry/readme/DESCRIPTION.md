Adds a **Request Information** button to each product page in the eCommerce shop.
Clicking the button opens a modal form where the visitor selects a request type
(*More Information* or *Quote*), fills in their contact details, and submits.

A CRM lead is created automatically from the submission, pre-linked to the
enquired product. Downstream glue modules can override
`ProductInquiryController._get_product_salesperson` to assign a specific
salesperson based on product-level ownership data.
