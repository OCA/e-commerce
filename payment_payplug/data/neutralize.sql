-- disable the Payplug payment provider
UPDATE payment_provider
   SET payplug_secret_key = NULL,
       payplug_client_secret = NULL;
