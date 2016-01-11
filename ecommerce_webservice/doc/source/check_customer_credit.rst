Details of check_customer_credit method
=======================================

Goal
----

Return the credit total amount of customers.

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
| method_name  | string          | ``check_customer_credit``                                          |
+--------------+-----------------+--------------------------------------------------------------------+
| shop_ident   | string          | Shop identifier                                                    |
+--------------+-----------------+--------------------------------------------------------------------+
| customer_ids | list of integer | Filter on a selection of customers.                                |
|              |                 |                                                                    |
|              |                 | If empty, returns all customers.                                   |
+--------------+-----------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a list of dictionaries of customer ids with their credits.

..  code-block:: python

    [{'id': 1, 'credit': 100},
     {'id': 2, 'credit': 0},
    ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    credits = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'shop_identifier',
        'check_customer_credit',
        [1, 5, 7]
        )
    print credits
    [{'id': 1, 'credit': 230},
     {'id': 5, 'credit': 550},
     {'id': 7, 'credit': 0},
    ]

PHP call example
----------------

..  code-block:: php
   :linenos:

   <?php

   require_once('ripcord/ripcord.php');

   // CREATE A CUSTOMER AND THEN UPDATE SOME FIELDS
   // FOR THIS NEWLY CREATED CUSTOMER

   $url = 'http://localhost:8069';
   $db = 'database';
   $username = "ecommerce_demo_external_user";
   $password = "dragon";
   $shop_identifier = "cafebabe";


   $common = ripcord::client($url."/openerp/xmlrpc/1/common");

   $uid = $common->authenticate($db, $username, $password, array());

   $models = ripcord::client("$url/openerp/xmlrpc/1/object");


   //create some customers

   $vals = array(
       'name'=>'Customer1',
       );

   $c1 = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'create_customer', array($shop_identifier, $vals));

   $vals = array(
       'name'=>'Customer2',
       );

   $c2 = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'create_customer', array($shop_identifier, $vals));

   // retrieve credit for those customers
   $customer_ids = array($c1, $c2);

   $records = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'check_customer_credit', array($shop_identifier, $customer_ids));

   var_dump($records);

   ?>

