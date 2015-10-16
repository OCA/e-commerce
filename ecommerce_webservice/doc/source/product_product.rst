Products Product API Details
============================

Goal
----

Return information about all product variants. The search can be filtered by search criteria and the returned information can be limited to a selection of fields.

If the eshop does not care about product templates, this is the only method that it will use for the products, because the returned data includes the data of the template of the variant as well.

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
| method_name | string                 | ``search_read_product_variant``                                     |
+-------------+------------------------+---------------------------------------------------------------------+
| shop_ident  | string                 | Shop identifier                                                     |
+-------------+------------------------+---------------------------------------------------------------------+
| domain      | list of tuples/strings | Search domain. See :doc:`_about_search_domains` chapter.            |
|             |                        |                                                                     |
|             |                        | Example: ``['sku = ABC']`` or ``[('sku', '=', 'ABC')]``             |
+-------------+------------------------+---------------------------------------------------------------------+
| fields      | list of strings        | If provided, the response returns only the asked fields.            |
|             |                        |                                                                     |
|             |                        | Example: ``['id', 'name', 'description']``                          |
|             |                        |                                                                     |
|             |                        | Otherwise, it will return all fields in ``product.template`` object |
+-------------+------------------------+---------------------------------------------------------------------+
| offset      | integer                | Set an offset for reading rows                                      |
+-------------+------------------------+---------------------------------------------------------------------+
| limit       | integer                | Limit number of returned rows                                       |
+-------------+------------------------+---------------------------------------------------------------------+
| order       | string                 | Change ordering of rows (example : ``'create_date asc'``)           |
+-------------+------------------------+---------------------------------------------------------------------+

Available Fields
----------------

**PRODUCT.PRODUCT OBJECT HAS THE SAME BASE FIELDS THAN PRODUCT.TEMPLATE OBJECT. SO HAVE A LOOK AT** :doc:`product_template` **TO HAVE THOSE BASE FIELDS.**


.. csv-table::
   :header: "name", "field description", "type", "available values", "required", "size", "translate", "standard/custom", "help"

    active,Active,boolean,,FALSE,,FALSE,standard,
    code,Internal Reference,char,,FALSE,,FALSE,standard,computed field. do not use
    color,Color Index,integer,,FALSE,,FALSE,standard,
    default_code,Internal Reference,char,,FALSE,64,FALSE,standard,
    delivery_count,Delivery,integer,,FALSE,,FALSE,standard,
    ean13,EAN13 Barcode,char,,FALSE,13,FALSE,standard,
    image,Image,binary,,FALSE,,FALSE,standard,base64 encoded
    image_medium,Medium-sized image,binary,,FALSE,,FALSE,standard,base64 encoded
    image_small,Small-sized image,binary,,FALSE,,FALSE,standard,base64 encoded
    incoming_qty,Incoming,float,,FALSE,,FALSE,standard,
    location_id,Location,FK to stock.location object,,FALSE,,FALSE,standard,
    lst_price,Public Price,float,,FALSE,,FALSE,standard,
    message_follower_ids,Followers,many2many,,FALSE,,FALSE,standard,DO NOT USE. ODOO MESSAGING FIELDS
    message_ids,Messages,one2many,,FALSE,,FALSE,standard,DO NOT USE. ODOO MESSAGING FIELDS
    message_is_follower,Is a Follower,boolean,,FALSE,,FALSE,standard,DO NOT USE. ODOO MESSAGING FIELDS
    message_summary,Summary,text,,FALSE,,FALSE,standard,DO NOT USE. ODOO MESSAGING FIELDS
    message_unread,Unread Messages,boolean,,FALSE,,FALSE,standard,DO NOT USE. ODOO MESSAGING FIELDS
    name_template,Template Name,char,,FALSE,128,FALSE,standard,
    orderpoint_ids,Minimum Stock Rules,one2many,,FALSE,,FALSE,standard,
    outgoing_qty,Outgoing,float,,FALSE,,FALSE,standard,
    packaging,Logistical Units,one2many,,FALSE,,FALSE,standard,
    partner_ref,Customer ref,char,,FALSE,,FALSE,standard,computed field. do not use
    price,Price,float,,FALSE,,FALSE,standard,
    price_extra,Variant Price Extra,float,,FALSE,,FALSE,standard,
    pricelist_id,Pricelist,many2one,,FALSE,,FALSE,standard,
    price_margin,Variant Price Margin,float,,FALSE,,FALSE,standard,
    product_tmpl_id,Product Template,FK to product.template object,,TRUE,,FALSE,standard,
    qty_available,Quantity On Hand,float,,FALSE,,FALSE,standard,
    reception_count,Reception,integer,,FALSE,,FALSE,standard,
    seller_delay,Supplier Lead Time,integer,,FALSE,,FALSE,standard,calculated fields from seller_ids field
    seller_id,Main Supplier,many2one,,FALSE,,FALSE,standard,
    seller_info_id,Supplier Info,many2one,,FALSE,,FALSE,standard,
    seller_qty,Supplier Quantity,float,,FALSE,,FALSE,standard,
    track_incoming,Track Incoming Lots,boolean,,FALSE,,FALSE,standard,
    track_outgoing,Track Outgoing Lots,boolean,,FALSE,,FALSE,standard,
    track_production,Track Manufacturing Lots,boolean,,FALSE,,FALSE,standard,
    valuation,Inventory Valuation,selection,"('manual_periodic', 'Periodical (manual)'),
    ('real_time','Real Time (automated)')",TRUE,,FALSE,standard,"If real-time valuation is enabled for a product, the system will automatically write journal entries corresponding to stock moves.
    The inventory variation account set on the product category will represent the current inventory value, and the stock input and stock output account will hold the counterpart moves for incoming and outgoing products."
    variants,Variants,char,,FALSE,64,FALSE,standard,
    virtual_available,Forecasted Quantity,float,,FALSE,,FALSE,standard,
    warehouse_id,Warehouse,FK to stock.warehouse object,,FALSE,,FALSE,standard,

Note: If an Odoo module adds fields, they will automatically be added to the API return.


Return values
^^^^^^^^^^^^^

Method returns a list of dictionnary. Each dictionnary corresponds to a product template matching domain criterion.

..  code-block:: python

     [
      {'id': 15, 'name': 'T-Shirt', 'default_code': 'ABC', ...},
      {'id': 16, 'name': 'Hat', 'default_code': 'DEF', ...},
       ...
      ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    templates = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'search_read_product_variant',
        'shop_identifier',
        ['sku = ABC', 'create_date > 2015-09-24 00:00:00']
        )
    print templates
    [{'id': 15, 'name': 'T-Shirt', 'default_code': 'ABC', ...}, ...]

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    <?php 
    
    require_once('ripcord/ripcord.php');
    
    $url = 'http://localhost:8069';
    $db = 'database';
    $username = "admin";
    $password = "admin";
    $shop_identifier = "cafebabe";
    
    
    $common = ripcord::client($url."/xmlrpc/common");
    
    $uid = $common->authenticate($db, $username, $password, array());
    
    $models = ripcord::client("$url/xmlrpc/object");
    
    $domain = array(
        array('name','ilike', 'USB'),
        );
    
    $fields = array('name', 'default_code');
    $all_fields = array();
    
    $records = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'search_read_product_variant', array($shop_identifier, $domain, $fields));
    
    var_dump($records);
    
    
    $records_all_fields = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'search_read_product_variant', array($shop_identifier, $domain, $all_fields));
    
    var_dump($records_all_fields);
    
    ?>


