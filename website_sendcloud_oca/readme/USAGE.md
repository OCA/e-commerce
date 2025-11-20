## Quickstart

In short this is how the module works:  
- the customer selects some products in the online shop. The products
  are added in the shopping Cart
- then the customer opens his shopping Cart and clicks on Process
  Checkout
- the customer chooses one of the delivery method that Sendcloud
  provides

## Service Point Picker

The module contains a link that opens the Service Point Picker
(javascript) in the website shopping Cart. The link is placed near the
selected Sendcloud Shipping Method. The link is visible in case:

> - the configuration in the Sendcloud panel has the Service Point flag
>   to True (in the Sendcloud integration config)
> - the Shipping Method selected in the picking is provided by Sendcloud
> - the Shipping Method has field sendcloud_service_point_input ==
>   "required"
> - all the criteria (from country, to country, weight) match with the
>   current order
> - the Shipping Method is set to "Published" in the website

## Case of multiple shops

TODO
