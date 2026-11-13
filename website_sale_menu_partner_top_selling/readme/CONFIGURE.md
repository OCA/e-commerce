To set the maximum number of products shown on the *My Regular
Products* page:

1.  Go to *Website \> Configuration \> Settings*, *eCommerce* section.
2.  Set *Regular Products Limit*. The default is 10.

The limit is stored in the `website_sale_menu_partner_top_selling.limit`
system parameter and is shared by all websites.

The *Regular Products Period (Days)* setting limits how far back orders
are counted: only orders from the last days are taken into account. The
default is 0, which counts all orders. It is stored in the
`website_sale_menu_partner_top_selling.period_days` system parameter.

The *Regular Products Menu Label* setting changes the label of the link
to the page in the shop and of the card on the customer portal. It is
translatable.

The *Customer Portal Card* setting shows a card linking to the page on
the customer portal home page. It is disabled by default.

For the *My Regular Products* link to appear in */shop*, enable either
the categories sidebar or the top categories bar. The top categories bar
is only displayed when the shop has eCommerce categories.
