When an order is placed from the website, the logged-in user is usually a
child contact of a company. Standard `website_sale` sets that contact as the
order customer (`partner_id`).

This module mirrors the backend `sale_partner_sale_contact` behaviour on the
website: the **parent company** becomes the order customer and the **contact**
is stored in the **Sale Contact** field (`sale_contact_partner_id`). Billing
and shipping addresses are left untouched.
