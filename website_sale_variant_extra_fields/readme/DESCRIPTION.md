The standard *Product Page Extra Fields* configuration lets a website manager
pick product fields to display on the shop product page. It only supports
char and binary fields on the product template, and the displayed value is
read once when the page loads, so it never updates when the customer switches
variants.

This module removes both limitations:

- product variant fields can be selected, in addition to product template
  fields;
- more field types are supported: numbers, dates, datetimes, dropdown
  (selection) values and linked records, in addition to char and binary
  fields;
- when a variant field is selected, its value refreshes live on the product
  page as soon as the customer picks a different combination of attributes.
  - decimal numbers are displayed with the number of decimals configured for the
  selected field.
