Errors
======

Errors are returned as standard XML-RPC errors with 2 attributes:
``faultCode`` and ``faultString``. ``faultCode`` contains an integer
which represents the type of error and ``faultString`` contains a
description of the error.

**Fault Codes**

+-----------+---------------------------------------------------------+
| faultCode | Description                                             |
+===========+=========================================================+
| 1         | Client error (malformed request, ...) or application    |
|           | internal error                                          |
+-----------+---------------------------------------------------------+
| 2         | Application / ORM-level errors (access errors,          |
|           | constraints, ...)                                       |
+-----------+---------------------------------------------------------+
| 3         | Login / password error                                  |
+-----------+---------------------------------------------------------+
