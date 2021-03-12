When a customer makes a purchase and do the checkout process, the VAT country
code can be selected separated from the code itself. This is useful in 2 ways:

- User is implicitly forced to input (select) a country with its code.
- Error in the VAT now only can be raised by an incorrect vat, not the absence
  of the country code, which usually confuses users.

If you change the country for the address and the VAT is empty, the VAT country
changes automatically too.
