Details of create_sale_order method
===================================

Goal
----

Create a sale order in Odoo giving necessary fields values

Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+--------------+-----------------+--------------------------------------------------------------------+
| Argument     | Type            | Comment                                                            |
+==============+=================+====================================================================+
| dbname       | string          | name of the database                                               |
+--------------+-----------------+--------------------------------------------------------------------+
| uid          | integer         | Id of the user making the call                                     |
+--------------+-----------------+--------------------------------------------------------------------+
| password     | string          | password of the user uid                                           |
+--------------+-----------------+--------------------------------------------------------------------+
| model        | string          | Always ``ecommerce.api.v1``                                        |
+--------------+-----------------+--------------------------------------------------------------------+
| method_name  | string          | ``create_sale_order``                                              |
+--------------+-----------------+--------------------------------------------------------------------+
| shop_ident   | string          | Shop identifier                                                    |
+--------------+-----------------+--------------------------------------------------------------------+
| values       | dictionary      | See below for details.                                             |
|              | of values       |                                                                    |
+--------------+-----------------+--------------------------------------------------------------------+

Sale order fields
*****************

+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| Name                | Type            | Comment                                                            | Required | Extra Infos                          |
+=====================+=================+====================================================================+==========+======================================+
| name                | string          | Order Reference                                                    | TRUE     | size=64                              |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| client_order_ref    | string          | Customer Reference                                                 | FALSE    | size=64                              |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| date_order          | date            | Date of the order                                                  | TRUE     | format = ``YYYY-mm-dd``              | 
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| note                | text            | Terms and conditions                                               | FALSE    |                                      |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| origin              | string          | Source document                                                    | FALSE    | size=64                              |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| partner_id          | integer (id)    | Odoo ID of the customer                                            | TRUE     | FK on res.partner object (customer)  |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| partner_invoice_id  | integer (id)    | Odoo ID of the invoice address                                     | FALSE    | FK on res.partner object (address)   |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| partner_shipping_id | integer (id)    | Odoo ID of the shipping address                                    | FALSE    | FK on res.partner object (address)   |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| payment_term*       | integer (id)    | Odoo ID of the payment term                                        | FALSE    | FK on account.payment.term object    |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| fiscal_position*    | integer (id)    | Odoo ID of the fiscal position                                     | FALSE    | FK on account.fiscal.position object |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+

\* for these fields, you have to manage the mapping between eshop id and Odoo ID from your side because no method exists to retrieve them from the API

Sale order line fields
**********************

+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| Name                | Type            | Comment                                                            | Required | Extra Infos                          |
+=====================+=================+====================================================================+==========+======================================+
| product_id          | integer (id)    | ID of the product                                                  | TRUE     | FK on product.product object         |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| name                | string          | Description of the product, if empty, use the Odoo one             | TRUE     | text (no limit)                      | 
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| price_unit          | float           | Unit price                                                         | TRUE     |                                      |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| discount            | float           | Discount (%)                                                       | FALSE    | default = 0                          |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| product_uom_qty     | float           | Quantity                                                           | TRUE     |                                      |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+
| sequence            | integer         | Sequence of the line (asc order, 0 is the first)                   | FALSE    | default = 10                         |
+---------------------+-----------------+--------------------------------------------------------------------+----------+--------------------------------------+


Return values
^^^^^^^^^^^^^

Method returns an integer corresponding to the Odoo ID of the sale order created.

..  code-block:: python

    10

Python call example
-------------------
..  code-block:: python
   :linenos:

    sale_order_id = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'create_sale_order',
        'shop_identifier',
        {'name': '10000532', 'partner_id', 154,
         'order_line': [{'product_id': 1, 'price_unit': 10.5, 'product_uom_qty': 2}]
         }
        )
    print sale_order_id
    10

PHP call example
----------------

..  code-block:: php
   :linenos:

   <?php

   require_once('ripcord/ripcord.php');


   $url = 'http://localhost:8069';
   $db = 'database';
   $username = "ecommerce_demo_external_user";
   $password = "dragon";
   $shop_identifier = "cafebabe";


   $common = ripcord::client($url."/openerp/xmlrpc/1/common");

   $uid = $common->authenticate($db, $username, $password, array());

   $models = ripcord::client("$url/openerp/xmlrpc/1/object");

   $vals = array(
       'name'=>'TEST',
       'partner_id'=>6,
       'partner_invoice_id'=>6,
       'partner_shipping_id'=>6,
       'payment_method_id'=>1,
       'order_line'=>array(array(
           'name'=>'test name line',
           'price_unit'=>54.6,
           'product_uom_qty'=>2,
           'product_id'=>49
           ))
       );

   $records = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'create_sale_order', array($shop_identifier, $vals));

   var_dump($records);

   ?>

