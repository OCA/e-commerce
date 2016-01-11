Details of search_read_customer and search_read_address methods
===============================================================

Goal
----

Return information about all customers and addresses.

The search can be filtered by search criteria and the returned information can be limited to a selection of fields.

Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+-------------+------------------------+---------------------------------------------------------------------+
| Argument    | Type                   | Comment                                                             |
+=============+========================+=====================================================================+
| dbname      | string                 | name of the database                                                |
+-------------+------------------------+---------------------------------------------------------------------+
| uid         | integer                | Id of the user making the call                                      |
+-------------+------------------------+---------------------------------------------------------------------+
| password    | string                 | password of the user uid                                            |
+-------------+------------------------+---------------------------------------------------------------------+
| model       | string                 | Always ``ecommerce.api.v1``                                         |
+-------------+------------------------+---------------------------------------------------------------------+
| method_name | string                 | ``search_read_customer`` or ``search_read_address``                 |
+-------------+------------------------+---------------------------------------------------------------------+
| shop_ident  | string                 | Shop identifier                                                     |
+-------------+------------------------+---------------------------------------------------------------------+
| domain      | list of tuples/strings | Search domain. See :doc:`_about_search_domains` chapter.            |
|             |                        |                                                                     |
|             |                        | Example: ``['name = ABC']`` or ``[('name', '=', 'ABC')]``           |
+-------------+------------------------+---------------------------------------------------------------------+
| fields      | list of strings        | If provided, the response returns only the asked fields.            |
|             |                        |                                                                     |
|             |                        | Example: ``['id', 'name', 'description']``                          |
|             |                        |                                                                     |
|             |                        | Otherwise, it will return all fields in ``res.partner`` object      |
+-------------+------------------------+---------------------------------------------------------------------+
| offset      | integer                | Set an offset for reading rows                                      |
+-------------+------------------------+---------------------------------------------------------------------+
| limit       | integer                | Limit number of returned rows                                       |
+-------------+------------------------+---------------------------------------------------------------------+
| order       | string                 | Change ordering of rows (example : ``'create_date asc'``)           |
+-------------+------------------------+---------------------------------------------------------------------+

Available Fields
----------------

.. csv-table::
   :header: name,field description,type,available values,required,size,translate,standard/custom,help
   
    active,Active,boolean,,FALSE,,FALSE,standard,
    bank_ids,Banks,one2many,,FALSE,,FALSE,standard,
    birthdate,Birthdate,char,,FALSE,64,FALSE,standard,
    category_id,Tags,many2many,,FALSE,,FALSE,standard,
    child_ids,Contacts,one2many,,FALSE,,FALSE,standard,
    city,City,char,,FALSE,128,FALSE,standard,
    color,Color Index,integer,,FALSE,,FALSE,standard,
    comment,Notes,text,,FALSE,,FALSE,standard,
    commercial_partner_id,Commercial Entity,many2one,,FALSE,,FALSE,standard,computed field
    company_id,Company,FK on res.company object,,FALSE,,FALSE,standard,
    contact_address,Complete Address,char,,FALSE,,FALSE,standard,computed field
    contract_ids,Contracts,one2many,,FALSE,,FALSE,standard,
    country,Country,FK on res.country object,,FALSE,,FALSE,standard,computed field
    country_id,Country,FK on res.country object,,FALSE,,FALSE,standard,
    credit,Total Receivable,float,,FALSE,,FALSE,standard,
    credit_limit,Credit Limit,float,,FALSE,,FALSE,standard,
    customer,Customer,boolean,,FALSE,,FALSE,standard,
    date,Date,date,,FALSE,,FALSE,standard,
    debit,Total Payable,float,,FALSE,,FALSE,standard,
    debit_limit,Payable Limit,float,,FALSE,,FALSE,standard,
    display_name,Name,char,,FALSE,,FALSE,standard,computed field
    ean13,EAN13,char,,FALSE,13,FALSE,standard,
    email,Email,char,,FALSE,240,FALSE,standard,
    employee,Employee,boolean,,FALSE,,FALSE,standard,
    fax,Fax,char,,FALSE,64,FALSE,standard,
    function,Job Position,char,,FALSE,128,FALSE,standard,
    has_image,unknown,boolean,,FALSE,,FALSE,standard,computed field
    image,Image,binary,,FALSE,,FALSE,standard,base64 encoded
    image_medium,Medium-sized image,binary,,FALSE,,FALSE,standard,base64 encoded
    image_small,Small-sized image,binary,,FALSE,,FALSE,standard,base64 encoded
    invoice_ids,Invoices,one2many,,FALSE,,FALSE,standard,
    is_company,Is a Company,boolean,,FALSE,,FALSE,standard,
    lang,Language,selection,,FALSE,,FALSE,standard,
    last_reconciliation_date,Latest Full Reconciliation Date,datetime,,FALSE,,FALSE,standard,
    message_follower_ids,Followers,many2many,,FALSE,,FALSE,standard,
    message_ids,Messages,one2many,,FALSE,,FALSE,standard,
    message_is_follower,Is a Follower,boolean,,FALSE,,FALSE,standard,
    message_summary,Summary,text,,FALSE,,FALSE,standard,
    message_unread,Unread Messages,boolean,,FALSE,,FALSE,standard,
    mobile,Mobile,char,,FALSE,64,FALSE,standard,
    name,Name,char,,TRUE,128,FALSE,standard,
    notification_email_send,Receive Messages by Email,selection,,TRUE,,FALSE,standard,
    opt_out,Opt-Out,boolean,,FALSE,,FALSE,standard,
    parent_id,Related Company,FK on res.partner object,,FALSE,,FALSE,standard,
    parent_name,Parent name,char,,FALSE,,FALSE,standard,computed field
    phone,Phone,char,,FALSE,64,FALSE,standard,
    property_account_payable,Account Payable,FK on account.account object,,TRUE,,FALSE,standard,
    property_account_position,Fiscal Position,FK on account.fiscal.position object,,FALSE,,FALSE,standard,
    property_account_receivable,Account Receivable,FK on account.account object,,TRUE,,FALSE,standard,
    property_payment_term,Customer Payment Term,FK on account.payment.term object,,FALSE,,FALSE,standard,
    property_product_pricelist,Sale Pricelist,FK on product.pricelist object,,FALSE,,FALSE,standard,
    property_stock_customer,Customer Location,FK on account.payment.term object,,FALSE,,FALSE,standard,
    property_stock_supplier,Supplier Location,FK on stock.location object,,FALSE,,FALSE,standard,
    property_supplier_payment_term,Supplier Payment Term,FK on stock.location object,,FALSE,,FALSE,standard,
    ref,Reference,char,,FALSE,64,FALSE,standard,
    ref_companies,Companies that refers to partner,one2many,,FALSE,,FALSE,standard,
    sale_order_count,# of Sales Order,integer,,FALSE,,FALSE,standard,
    sale_order_ids,Sales Order,one2many,,FALSE,,FALSE,standard,
    signup_expiration,Signup Expiration,datetime,,FALSE,,FALSE,standard,
    signup_token,Signup Token,char,,FALSE,,FALSE,standard,
    signup_type,Signup Token Type,char,,FALSE,,FALSE,standard,
    signup_url,Signup URL,char,,FALSE,,FALSE,standard,
    signup_valid,Signup Token is Valid,boolean,,FALSE,,FALSE,standard,
    state_id,State,FK on res.country.state object,,FALSE,,FALSE,standard,
    street,Street,char,,FALSE,128,FALSE,standard,
    street2,Street2,char,,FALSE,128,FALSE,standard,
    supplier,Supplier,boolean,,FALSE,,FALSE,standard,
    title,Title,FK on res.partner.title object,,FALSE,,FALSE,standard,
    type,Address Type,selection,,FALSE,,FALSE,standard,
    tz,Timezone,selection,,FALSE,,FALSE,standard,
    tz_offset,Timezone offset,char,,FALSE,,FALSE,standard,
    use_parent_address,Use Company Address,boolean,,FALSE,,FALSE,standard,
    user_id,Salesperson,FK on res.partner object,,FALSE,,FALSE,standard,
    user_ids,Users,one2many,,FALSE,,FALSE,standard,
    vat,TIN,char,,FALSE,32,FALSE,standard,
    website,Website,char,,FALSE,64,FALSE,standard,
    zip,Zip,char,,FALSE,24,FALSE,standard,



Return values
^^^^^^^^^^^^^

Method returns a list of dictionaries. Each dictionary corresponds to a
customer or an address (according to method called) matching domain
criteria.

..  code-block:: python

    [
     {'id': 15, 'name': 'Jane Doe', 'street': 'Maple Road', ...},
     ...
     ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    customers = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'search_read_customer',
        'shop_identifier',
        ['create_date > 2015-09-24 00:00:00']
        )
    print customers
    [
     {'id': 15, 'name': 'Jane Doe', 'street': 'Maple Road', ...},
     ...
     ]


    addresses = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'search_read_address',
        'shop_identifier',
        ['create_date > 2015-09-24 00:00:00', 'parent_id = 15'],
        ['street', 'city']
        )
    print addresses
    [
     {'id': 16, 'street': 'Maple Road', 'city': 'Junction City'},
     ...
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

   $domain = array(
       array('name','=', 'Agrolait'),
       );

   $fields = array('name', 'ref');

   $records = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'search_read_customer', array($shop_identifier, $domain, $fields));

   var_dump($records);

   $domain_address = array(
       array('name','ilike', 'luc'),
       );

   $fields_address = array('name', 'ref', 'parent_id');

   $records_address = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'search_read_address', array($shop_identifier, $domain_address, $fields_address));

   var_dump($records_address);

   ?>
