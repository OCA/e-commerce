Details of create_customer() method
===================================

Goal
----

Create a customer in OpenERP giving necessary fields values

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
| method_name  | string          | ``create_customer``                                                |
+--------------+-----------------+--------------------------------------------------------------------+
| shop_ident   | string          | Shop identifier                                                    |
+--------------+-----------------+--------------------------------------------------------------------+
| values       | dictionnary     | See below for details.                                             |
|              | of values       |                                                                    |
+--------------+-----------------+--------------------------------------------------------------------+

Values parameters
*****************

.. csv-table::
   :header: Name,Type,Comment,Required,Extra Infos
   
    name,string,Name,TRUE,size=128
    active,boolean,Active?,FALSE,default=True
    street,string,Street,FALSE,size=128
    street2,string,Street2,FALSE,size=128
    city,string,City,FALSE,size=128
    zip,string,ZIP,FALSE,size=24
    country,string,Country Code,FALSE,size=2
    phone,string,Phone,FALSE,size=64
    mobile,string,Mobile,FALSE,size=64
    fax,string,Fax,FALSE,size=64
    email,string,email,FALSE,size=240
    website,string,Website URL,FALSE,size=64
    ref,string,Customer code,FALSE,size=64
    comment,string,Comments (text),FALSE,


Return values
^^^^^^^^^^^^^

Method returns an integer corresponding to the OpenERP ID of the customer created.

..  code-block:: python

    54

Python call example
-------------------
..  code-block:: python
   :linenos:

    partner_id = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'create_customer',
        'shop_identifier',
        {'name': 'Jane Doe'}
        )
    print partner_id
    54

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    <?php 
    
    require_once('ripcord/ripcord.php');
    
    // CREATE A CUSTOMER
    
    $url = 'http://localhost:8069';
    $db = 'database';
    $username = "admin";
    $password = "admin";
    $shop_identifier = "cafebabe";
    
    
    $common = ripcord::client($url."/xmlrpc/common");
    
    $uid = $common->authenticate($db, $username, $password, array());
    
    $models = ripcord::client("$url/xmlrpc/object");
    
    $vals = array(
        'name'=>'Customer1',
        );
    
    $records = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'create_customer', array($shop_identifier, $vals));
    
    var_dump($records);
    
    ?>

