Setup
=====

Short guide for installation and configuration of the module.

Configuration of users and access rights
----------------------------------------

The web-service uses 2 users.

* One public user that will be used for XML-RPC
* One internal user that will be used for all the accesses to the models
  internally

Public user
^^^^^^^^^^^

* This user must have a strong password. It will be used for the
  web-service connections.
* It should have the group ``Ecommerce API``, no more rights required,
  because the operations on the models will be done with the internal
  user.

Internal user
^^^^^^^^^^^^^

* This user should not have a password. Nobody should be able to login
  with it. It will be used internally by the Web-Service.
* It is automatically created by the module with the name ``Ecommerce
  Default Internal User``
* It should have the group ``Own Ecommerce API Shop internal``. This
  group inherits all the ``Sales Manager`` accesses which should cover
  all the permissions needed for the Web-Service. If any access is
  missing, they should be granted to this user.

Configuration of the Ecommerce web-service
------------------------------------------

1. Go in ``Ecommerce API``.
2. Create a new ``Shop``. It proposes an identifier for the shop that
   will need to be communicated to the clients to allow them to access
   to this shop.
3. On the shop, configure the public and internal users configured in
   the previous chapter.
4. The selected ``Sale Shop`` will be the one in which the sales orders
   are created.
5. You can choose to enable or disable logs.

Based on this configuration, the XML-RPC client should use the following
parameters:

* login: the public login and password created previously
* shop identifier: the shop identifier of the new shop

If a web-service is needed for another sales shop, a new Ecommerce shop
must be created.

