Products Category API Details
=============================

Goal
----

Return information about all product categories. The search can be
filtered by search criteria and the returned information can be limited
to a selection of fields.

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
| method_name | string                 | ``search_read_product_category``                                    |
+-------------+------------------------+---------------------------------------------------------------------+
| shop_ident  | string                 | Shop identifier                                                     |
+-------------+------------------------+---------------------------------------------------------------------+
| domain      | list of tuples/strings | Search domain. See :doc:`_about_search_domains` chapter.            |
|             |                        |                                                                     |
|             |                        | Example: ``['name = ABC']`` or ``[('name', '=', 'ABC')]``           |
+-------------+------------------------+---------------------------------------------------------------------+
| fields      | list of strings        | If provided, the response returns only the asked fields.            |
|             |                        |                                                                     |
|             |                        | Example: ``['id', 'name', 'parent_id']``                            |
|             |                        |                                                                     |
|             |                        | Otherwise, it will return all fields in ``product.category`` object |
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
   :header: "name", "field description", "type", "available values", "required", "size", "translate", "standard/custom", "help"

    complete_name,Name,char,,False,,False,standard,
    name,Name,char,,True,,True,standard,
    type,Category Type,selection,view or normal,False,,False,standard,
    parent_id,Parent Category,many2one,,False,,False,standard,
    property_account_expense_categ,Expense Account,many2one,,False,,False,standard,
    property_account_income_categ,Income Account,many2one,,False,,False,standard,
    property_stock_account_input_categ,Stock Input Account,many2one,,False,,False,standard,
    property_stock_account_output_categ,Stock Output Account,many2one,,False,,False,standard,
    property_stock_journal,Stock Journal,many2one,,False,,False,standard,
    property_stock_valuation_account_id,Stock Valuation Account,many2one,,False,,False,standard,
    sequence,Sequence,integer,,False,,False,standard,
    child_id,Child Categories,one2many,,False,,False,standard,
    parent_left,Left Parent,integer,,False,,False,standard,
    parent_right,Right Parent,integer,,False,,False,standard,

Note: If an Odoo module adds fields, they will automatically be added to the API return.


Return values
^^^^^^^^^^^^^

Method returns a list of dictionaries. Each dictionary corresponds to a
product category matching domain criteria.

..  code-block:: python

     [
      {'id': 15, 'name': 'Services',  ...},
      {'id': 16, 'name': 'Products', ...},
       ...
      ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    templates = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'search_read_product_category',
        'shop_identifier',
        ['id = 5']
        )
    print templates
    [{'id': 5, 'name': 'Services', ...}, ...]

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

   $domain = array(
       array('name','ilike', 'Services'),
       );

   $fields = array('name', 'type');
   $all_fields = array();

   $records = $models->execute_kw($db, $uid, $password,
       'ecommerce.api.v1', 'search_read_product_category', array($shop_identifier, $domain, $fields));

   var_dump($records);

   ?>
